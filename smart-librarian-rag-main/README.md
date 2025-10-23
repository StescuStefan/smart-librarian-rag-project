# 📚 Smart Librarian – AI Book Chatbot

Smart Librarian is a full-stack AI-powered book chatbot that offers personalized recommendations, full book summaries, and multimedia enhancements like text-to-speech and image generation.

![Preview](preview.png)

---

## 🚀 Features

- 🤖 **Ask anything**: Type or speak your question to receive personalized book recommendations.
- 📖 **Get summaries**: Search for full book summaries by title.
- 🔊 **Text-to-Speech**: Convert responses and summaries into playable audio.
- 🎨 **Image Generation**: Generate DALL·E 3 book-cover-style images for both responses and summaries.
- 🎤 **Speech-to-Text**: Speak into your mic and transcribe questions or titles directly.

---

## 🧠 Powered by

- `OpenAI GPT-4o-mini` for book recommendation
- `OpenAI text-embedding-3-small` + `ChromaDB` for RAG-based semantic retrieval
- `OpenAI DALL·E 3` for image generation
- `Google Cloud TTS (neutral voice)` for free tier text-to-speech
- `Google Cloud STT` for microphone transcription
- Frontend: `React + Vite + TailwindCSS`
- Backend: `FastAPI` with CORS, TTS/STT endpoints, and secure OpenAI/Google calls

---

## 🔐 Environment Variables (`.env`)

Make sure to create a `.env` file in your **backend** root directory with the following keys:

```env
OPENAI_API_KEY=your-openai-key-here
GOOGLE_APPLICATION_CREDENTIALS=your-google-credentials.json
```

> ⚠️ Don’t forget to add `.env` and `*.json` to `.gitignore` before pushing to GitHub!

---

## 🗂️ Folder Structure (Frontend)

```
📦frontend
 ┣ 📂components
 ┃ ┣ 📜AskForm.jsx
 ┃ ┣ 📜SummaryViewer.jsx
 ┣ 📂utils
 ┃ ┣ 📜api.js
 ┃ ┣ 📜speech.js
 ┣ 📜App.jsx
 ┣ 📜main.jsx
 ┣ 📜index.css
 ┣ 📜.env (ignored)
```

## 🗂️ Folder Structure (Backend)

```
📦backend
 ┣ 📂data
 ┃ ┣ 📜book_summaries_dict.py
 ┣ 📜backend_main.py
 ┣ 📜embed_books.py
 ┣ 📜.env (ignored)
 ┣ 📜stt_usage.json (auto-generated)
```

---

## 🛠️ Setup

### 📦 Install Dependencies

```bash
# Backend
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1 #terminal
pip install -r requirements.txt

# Frontend
cd frontend
npm install
```

### 🧪 Run the App

```bash
# Start backend (with uvicorn)
uvicorn backend_main:app --reload

# Start frontend
npm run dev
```

---

## 📌 Notes

- You must **enable Google Cloud TTS/STT APIs** and use **standard models** only (free tier).
- DALL·E 3 requests use `quality="standard"` and are generated as `book cover style` prompts.
- The app supports both **English and Romanian** theme/topic detection.
- App styling follows your provided TailwindCSS classes exactly (unchanged).

---

## 📄 License

This project is for educational/training purposes.
