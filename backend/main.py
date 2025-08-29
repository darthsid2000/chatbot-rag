from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List
from dotenv import load_dotenv
from chains import ask

load_dotenv()

app = FastAPI(title="Wiki RAG")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    session_id: str
    question: str
    top_k: int = 4

class Source(BaseModel):
    title: str
    chunk_id: int | None = None
    source: str | None = None

class ChatResponse(BaseModel):
    answer: str
    sources: List[Source] = Field(default_factory=list)

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest):
    out = ask(req.session_id, req.question, k=req.top_k)
    return ChatResponse(answer=out["answer"], sources=out["sources"])