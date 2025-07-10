# main.py
import os
from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from pymongo import MongoClient
import httpx

# 1) Load .env file
load_dotenv()  # looks for .env in cwd

# 2) Read env vars and guard
MONGO_URI    = os.getenv("MONGODB_URI")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if not MONGO_URI:
    raise RuntimeError(" MONGODB_URI is not set in .env")
if not GROQ_API_KEY:
    raise RuntimeError(" GROQ_API_KEY is not set in .env")

# 3) MongoDB client
client     = MongoClient(MONGO_URI)
db         = client.sample_mflix
collection = db.movies

# 4) FastAPI app + CORS
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # dev only!
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 5) Health check
@app.get("/")
async def health_check():
    return {"message": "Movie API with Groq is live!"}

# 6) List movies
@app.get("/movies")
async def list_movies():
    docs = collection.find({}, {"title": 1, "plot": 1}).limit(10)
    return [
        {"title": d.get("title"), "description": d.get("plot", "No description")}
        for d in docs
    ]

# 7) Chat endpoint
@app.post("/chat")
async def chat(request: Request):
    body     = await request.json()
    question = body.get("question", "").strip()
    if not question:
        return {"answer": "Please ask a valid question."}

    # build context from the first 10 plots
    docs = collection.find({}, {"title": 1, "plot": 1}).limit(10)
    context = "\n".join(f"Title: {d.get('title')}\nPlot: {d.get('plot','N/A')}"
                        for d in docs)

    payload = {
        "model": "meta-llama/llama-4-scout-17b-16e-instruct",
        "messages": [
            {"role": "system", "content": f"You are a movie assistant.\n{context}"},
            {"role": "user",   "content": question},
        ]
    }
    headers = {
        "Content-Type":  "application/json",
        "Authorization": f"Bearer {GROQ_API_KEY}",
    }

    try:
        async with httpx.AsyncClient() as client:
            res = await client.post(
                "https://api.groq.com/openai/v1/chat/completions",
                json=payload, headers=headers
            )
            res.raise_for_status()
            data   = res.json()
            answer = data["choices"][0]["message"]["content"].strip()
            return {"answer": answer}
    except Exception as e:
        # let’s bubble up the real error for now
        return {"answer": f"Error: {e}"}