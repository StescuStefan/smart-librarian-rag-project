from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Any
import os
from fastapi import Request
from fastapi.responses import JSONResponse
from google.cloud import texttospeech
from uuid import uuid4
from fastapi.staticfiles import StaticFiles
from dotenv import load_dotenv
from openai import OpenAI
import chromadb
from chromadb.utils import embedding_functions
from fastapi.middleware.cors import CORSMiddleware
from data.book_summaries_dict import book_summaries_dict
from fastapi import Body
from fastapi.responses import JSONResponse
from google.cloud import speech_v1 as speech
from pydub import AudioSegment
import io, json, time, pathlib
from fastapi import File, UploadFile, Form

# === STT usage guard (local counter) ===
STT_USAGE_FILE = pathlib.Path("./stt_usage.json")
# Google free tier: 60 minutes/month for Standard model. We'll keep a safety buffer.
FREE_TIER_SECONDS = 55 * 60  # 55 minutes (safety headroom)

def _load_stt_usage():
    if STT_USAGE_FILE.exists():
        try:
            data = json.loads(STT_USAGE_FILE.read_text(encoding="utf-8"))
            # reset monthly if needed (very simple reset on month change)
            now = time.gmtime()
            if data.get("year") != now.tm_year or data.get("month") != now.tm_mon:
                return {"seconds": 0, "year": now.tm_year, "month": now.tm_mon}
            return data
        except Exception:
            pass
    now = time.gmtime()
    return {"seconds": 0, "year": now.tm_year, "month": now.tm_mon}

def _save_stt_usage(seconds_total: int):
    now = time.gmtime()
    STT_USAGE_FILE.write_text(
        json.dumps({"seconds": seconds_total, "year": now.tm_year, "month": now.tm_mon}),
        encoding="utf-8"
    )

def _estimate_duration_seconds(file_bytes: bytes, filename: str, content_type: str) -> float:
    """
    Best-effort duration estimator using pydub.
    Works well if FFmpeg is installed for mp3/ogg; WAV works without FFmpeg.
    Falls back to 0 if it can't parse (we'll allow but warn in logs).
    """
    try:
        fileobj = io.BytesIO(file_bytes)
        lower_name = (filename or "").lower()
        ct = (content_type or "").lower()

        if lower_name.endswith(".wav") or "wav" in ct:
            audio = AudioSegment.from_wav(fileobj)
        elif lower_name.endswith(".mp3") or "mpeg" in ct or "mp3" in ct:
            audio = AudioSegment.from_file(fileobj, format="mp3")
        elif lower_name.endswith(".ogg") or "ogg" in ct:
            audio = AudioSegment.from_file(fileobj, format="ogg")
        elif lower_name.endswith(".webm") or "webm" in ct:
            audio = AudioSegment.from_file(fileobj, format="webm")
        else:
            # Try generic decode (needs FFmpeg)
            audio = AudioSegment.from_file(fileobj)

        return float(len(audio) / 1000.0)  # milliseconds -> seconds
    except Exception as e:
        print(f"⚠️ Could not estimate duration (will not block on quota): {e}")
        return 0.0

# Load API key from .env
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Connect to ChromaDB (must match embed_books.py location)
chroma_client = chromadb.PersistentClient(path="./chroma_storage")

# Setup embedding function
embedding_fn: Any = embedding_functions.OpenAIEmbeddingFunction(
    api_key=os.getenv("OPENAI_API_KEY"),
    model_name="text-embedding-3-small"
)

# Load the same collection used during embedding
collection = chroma_client.get_or_create_collection(
    name="book_summaries",
    embedding_function=embedding_fn
)

# Tool: hardcoded full summaries
book_summaries = {title: data["summary"] for title, data in book_summaries_dict.items()}

# FastAPI app
app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # React dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request models
class AskRequest(BaseModel):
    question: str

class SummaryRequest(BaseModel):
    title: str

# Function to detect inappropriate input
def is_inappropriate(text: str) -> bool:
    banned_words = [
        # English slurs/examples (partial)
        "slur1", "slur2", "offensive", "inappropriate",
        "idiot", "stupid", "dumb", "fool",
        "racist", "sexist", "homophobic", "nazi",
        "bigot", "asshole", "dickhead", "dick", "penis", "shit", "crap", "slut", "hoe", "bitch",
        "fuck you", "f you", "fuck",
        # Romanian examples
        "prost", "idiot", "tampit", "bou",
        "jeg", "muist", "curva", "zdreanta", "dracu", "naiba", "nesimtit", "nesimtire", "nesimtita", "nesimtitule", "nesimtitulei", "nesimtitului", "nesimtitilor",
        "fraiere", "tampitule", "prostule", "cacatule", "muie", "sugi pula", "sugi", "pula"
    ]
    lower_text = text.lower()
    return any(banned_word in lower_text for banned_word in banned_words)

# Route: Ask a question and get a recommended book
@app.post("/ask")
def ask_question(payload: AskRequest):
    if is_inappropriate(payload.question):
        return {"response": "⚠️ Întrebarea ta conține limbaj nepotrivit și nu poate fi procesată. / Your question contains inappropriate language."}

    query_embedding = embedding_fn([payload.question])[0]

    print("❓ USER QUESTION:", payload.question)
    print("🔎 QUERY EMBEDDING LENGTH:", len(query_embedding))

    print("📂 Stored themes in DB:")
    meta_data = collection.get().get("metadatas")
    if meta_data:
        for meta in meta_data:
            print("-", meta["themes"])
    else:
        print("⚠️ No metadata found.")

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=3
    )

    print("📄 MATCHING DOCS:", results["documents"])

    if not results["documents"] or not results["documents"][0]:
        return {"response": "Sorry, I couldn't find any relevant books."}

    context_chunks = results["documents"][0]
    context = "\n".join(context_chunks)

    chat_response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a helpful book recommendation assistant."},
            {"role": "user", "content": f"Here are some book summaries:\n{context}\n\nBased on this, what book would you recommend for: {payload.question}?"}
        ],
        temperature=0.7,
        max_tokens=300
    )

    return {"response": chat_response.choices[0].message.content}

# Route: Get full summary by book title
@app.post("/summary")
def get_summary(payload: SummaryRequest):
    summary = book_summaries.get(payload.title)
    if summary:
        return {"title": payload.title, "summary": summary}
    else:
        return {"error": "Book title not found"}

@app.post("/tts")
async def text_to_speech(request: Request):
    data = await request.json()
    text = data.get("text")

    if not text:
        return JSONResponse(content={"error": "No text provided"}, status_code=400)

    # Init Google TTS client
    client = texttospeech.TextToSpeechClient()

    input_text = texttospeech.SynthesisInput(text=text)

    voice = texttospeech.VoiceSelectionParams(
        language_code="en-US",  # Or "ro-RO" for Romanian
        ssml_gender=texttospeech.SsmlVoiceGender.NEUTRAL
    )

    audio_config = texttospeech.AudioConfig(
        audio_encoding=texttospeech.AudioEncoding.MP3
    )

    response = client.synthesize_speech(
        input=input_text,
        voice=voice,
        audio_config=audio_config
    )

    # Save audio to /static/audio
    audio_id = str(uuid4())
    audio_dir = "static/audio"
    os.makedirs(audio_dir, exist_ok=True)
    file_path = os.path.join(audio_dir, f"{audio_id}.mp3")

    with open(file_path, "wb") as out:
        out.write(response.audio_content)

    return {"audio_url": f"/static/audio/{audio_id}.mp3"}

# Generate image
@app.post("/generate-image")
async def generate_image(data: dict = Body(...)):
    prompt = data.get("prompt", "")
    if not prompt:
        return JSONResponse(status_code=400, content={"error": "Prompt is required"})

    # Modify prompt to enforce book cover style
    book_cover_prompt = f"Create a detailed book cover illustration for the following: {prompt}"

    try:
        response = client.images.generate(
            model="dall-e-3",  # You can switch to "dall-e-2" if needed
            prompt=book_cover_prompt,
            size="1024x1024",
            quality="standard",
            n=1
        )

        if not response or not response.data or not response.data[0].url:
            return JSONResponse(status_code=500, content={"error": "No image returned from OpenAI."})

        image_url = response.data[0].url
        return {"image_url": image_url}

    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})
    
@app.post("/stt")
async def speech_to_text(
    file: UploadFile = File(...),
    language: str = Form("en-US")  # allow "ro-RO" too
):
    """
    Accepts an audio file (prefer WAV/LINEAR16). Uses Google STT Standard model.
    Enforces a local monthly quota (55 min safety headroom).
    """

    # --- Read file ---
    file_bytes = await file.read()

    # --- Estimate duration for quota ---
    est_sec = _estimate_duration_seconds(
    file_bytes,
    file.filename or "",         # ensure str
    file.content_type or ""      # ensure str
)
    usage = _load_stt_usage()
    projected = usage["seconds"] + int(est_sec)

    if projected > FREE_TIER_SECONDS:
        return JSONResponse(
            status_code=429,
            content={
                "error": "STT free-tier limit reached for this month (local guard). Try next month or lower usage.",
                "used_seconds": usage["seconds"],
                "estimated_this_request": est_sec,
                "limit_seconds": FREE_TIER_SECONDS,
            },
        )

    # --- Build Google STT request (Standard model only) ---
    client_stt = speech.SpeechClient()

    # Try to guess encoding — safest is to recommend WAV/LINEAR16.
    # If you always send WAV, this is correct:
    encoding = speech.RecognitionConfig.AudioEncoding.LINEAR16
    sample_rate_hz = None  # let Google infer if possible

    # If you want to “auto” based on MIME: uncomment below, but LINEAR16 WAV is the most reliable.
    # ct = (file.content_type or "").lower()
    # if "mp3" in ct or file.filename.lower().endswith(".mp3"):
    #     encoding = speech.RecognitionConfig.AudioEncoding.MP3
    # elif "ogg" in ct or file.filename.lower().endswith(".ogg"):
    #     encoding = speech.RecognitionConfig.AudioEncoding.OGG_OPUS

    audio = speech.RecognitionAudio(content=file_bytes)
    config = speech.RecognitionConfig(
        language_code=language,         # "en-US" or "ro-RO"
        enable_automatic_punctuation=True,
        use_enhanced=False,             # <-- ensures Standard (free-tier eligible)
        model="default",                # <-- Standard model
        encoding=encoding,
        sample_rate_hertz=sample_rate_hz if sample_rate_hz else 0,
        audio_channel_count=1,
    )

    # --- Sync recognition (suitable for short clips) ---
    try:
        response = client_stt.recognize(config=config, audio=audio)
        transcript = " ".join([alt.transcript for r in response.results for alt in r.alternatives]) or ""

        # Update quota only if recognition succeeded and we had a duration estimate
        if est_sec > 0:
            usage["seconds"] += int(est_sec)
            _save_stt_usage(usage["seconds"])

        return {"text": transcript, "seconds_counted": int(est_sec), "quota_seconds_used": usage["seconds"]}
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})
