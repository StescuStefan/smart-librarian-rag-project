import os
import uuid
from dotenv import load_dotenv
import chromadb
from chromadb.utils import embedding_functions
from openai import OpenAI
from typing import Any
from data.book_summaries_dict import book_summaries_dict

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Embedding function
embedding_fn: Any = embedding_functions.OpenAIEmbeddingFunction(
    api_key=os.getenv("OPENAI_API_KEY"),
    model_name="text-embedding-3-small"
)

# Persistent ChromaDB
chroma_client = chromadb.PersistentClient(path="./chroma_storage")
collection = chroma_client.get_or_create_collection(
    name="book_summaries",
    embedding_function=embedding_fn
)

if __name__ == "__main__":
    # Prepare documents from the dictionary
    documents = []
    metadatas = []
    ids = []

    for title, data in book_summaries_dict.items():
        summary = data["summary"]
        themes = ", ".join(data["themes"])
        full_text = f"This book covers themes like {themes}. Summary: {summary}. It is a great choice for readers interested in {themes}."


        documents.append(full_text)
        metadatas.append({"title": title, "themes": themes})
        ids.append(str(uuid.uuid4()))

    # Optional: wipe old data (safely)
    existing_ids = collection.get()["ids"]
    if existing_ids:
        collection.delete(ids=existing_ids)
        print(f"🧹 Deleted {len(existing_ids)} old records from collection.")
    else:
        print("📭 Collection was already empty.")

    # Add new documents
    collection.add(
        documents=documents,
        metadatas=metadatas,
        ids=ids
    )

    # Debug output
    print(f"✅ Embedded and stored {len(documents)} book summaries.")
    print("📦 Stored docs count:", collection.count())

    metas = collection.get().get("metadatas")
    if metas:
        print("📚 Stored titles:", [m["title"] for m in metas])
    else:
        print("⚠️ No metadata found in collection.")
