import uuid
import os
from dotenv import load_dotenv
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from database import get_db, get_similarity
from auth import get_current_user
from crud import save_message
import ollama
from khmerns import tokenize, normalize
from embedding.metadata import get_tagging

import vertexai
from vertexai.generative_models import GenerativeModel

load_dotenv()

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = r"D:\AUPP\Project-Github\machine_learning_final_project\ocr-for-extraction-5f1d4479787d.json"
vertexai.init(project="ocr-for-extraction", location="us-central1")

model = GenerativeModel("gemini-2.0-flash")

router = APIRouter(prefix="/chat", tags=["Chat"])


PROMPT = '''
You are a medical assistant specializing in sexually transmitted diseases (STD/STI) in the context of Cambodia. You must only use the information explicitly provided to you, including disease descriptions, tags, and structured data. Do not introduce outside knowledge, assumptions, or general medical advice beyond the provided content. Before answering, verify whether the available information is sufficient. If it is not sufficient, respond with a brief apology and state that there is not enough information to provide a reliable response, then advise the user to seek professional medical care.

Your tone must be polite, calm, supportive, and empathetic, as users may be asking questions during stressful or sensitive situations. Avoid sounding blunt, robotic, or alarming. Responses must be short, concise, and written with correct grammar and formal spelling. Only include information that is directly relevant to the disease and tags provided, and avoid adding unrelated explanations or educational content.

If the user writes in Khmer, respond in Khmer. Medical terms should remain in English if no Khmer translation has been provided. Maintain formal and clear wording in both English and Khmer. You must never diagnose users, never conclude that they have a disease, and never estimate probability or confirm infection. Always use neutral phrasing and encourage users to consult a healthcare professional for proper evaluation. Each response should remain brief, ideally within three to five short sentences, with no speculation, no assumptions, and no unnecessary elaboration. Your goal is to provide supportive, accurate, and concise STD/STI-related guidance strictly within the provided Cambodia-focused information while prioritizing user safety and professional medical consultation.

'''

class ChatRequest(BaseModel):
    query: str
    media_context: str | None = None
    session_id: str | None = None
    top_k: int = 5


@router.post("/text")
async def chat_text(
    request: ChatRequest,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db),       # ← add this
):
    if not request.query.strip() and not request.media_context:
        raise HTTPException(status_code=400, detail="Query cannot be empty.")

    full_query = request.query
    if request.media_context:
        full_query = f"{request.media_context}\n\nUser question: {request.query}".strip()

    query = tokenize(normalize(full_query))
    segmented_query = ""
    for q in query:
        segmented_query += q
    
    full_query_tagged = get_tagging(segmented_query)
    embedded_query = ollama.embed(
        model = "bge-m3",
        input= segmented_query
    )

    similarity_search = get_similarity(db, embedded_query.embeddings, k = 5)

    full_prompt = f"""
        Role: {PROMPT}
        Query: {segmented_query}
        Tags: {full_query_tagged}
        Answer: {similarity_search}
    """

    response = model.generate_content(full_prompt)
    answer = response.text.strip()

    if current_user:
        session_id = request.session_id or str(uuid.uuid4())
        save_message(db, current_user.user_id, session_id, "user", full_query, "text")
        save_message(db, current_user.user_id, session_id, "bot", answer, "text")
    else:
        session_id = None

    return {
        "response": answer,
        "sources": [],
        "session_id": session_id,
        "saved": current_user is not None,
    }
