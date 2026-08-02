from fastapi import APIRouter
from pydantic import BaseModel

from app.services.chroma_service import collection
from app.services.gemini_service import generate_summary

router = APIRouter()


class ChatRequest(BaseModel):
    question: str


@router.post("/chat")
def chat(request: ChatRequest):

    # Search ChromaDB
    results = collection.query(
        query_texts=[request.question],
        n_results=3
    )

    # Combine retrieved documents
    context = ""

    if results["documents"]:
        for doc in results["documents"][0]:
            context += doc + "\n\n"

    # Create prompt
    prompt = f"""
You are an Enterprise AI Research Assistant.

Answer ONLY using the information below.

Context:
{context}

Question:
{request.question}

If the answer is not present in the context, say:
'I don't have enough information in the stored research.'
"""

    # Generate answer
    answer = generate_summary(prompt)

    return {
        "question": request.question,
        "answer": answer
    }