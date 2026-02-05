"""
DocChatAI Backend API
FastAPI application for RAG-based document chatbot.
"""

from fastapi import FastAPI, UploadFile, File, HTTPException, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from typing import List, Optional
import uuid

from config import get_settings
from models import (
    LoginRequest, LoginResponse,
    DocumentResponse, DocumentListResponse,
    ChatRequest, ChatResponse, NoSourceResponse,
    DashboardStats, BaseResponse
)
from services import documents as doc_service
from services import embeddings as embed_service
from services import chat as chat_service
from services import database as db_service


settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler."""
    print("🚀 DocChatAI Backend starting...")
    yield
    print("👋 DocChatAI Backend shutting down...")


app = FastAPI(
    title="DocChatAI API",
    description="RAG-based document chatbot API",
    version="1.0.0",
    lifespan=lifespan
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============ Health Check ============

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "DocChatAI API"}


# ============ Auth Endpoints ============

@app.post("/api/auth/login", response_model=LoginResponse)
async def login(request: LoginRequest):
    """
    User login endpoint.
    Note: In production, this would use Supabase Auth.
    """
    # For demo purposes, accept any credentials
    # In production, use Supabase Auth
    return LoginResponse(
        success=True,
        access_token=f"demo_token_{uuid.uuid4()}",
        user={
            "id": str(uuid.uuid4()),
            "email": request.email,
            "full_name": "Demo Kullanıcı",
            "role": "admin",
            "org_id": "00000000-0000-0000-0000-000000000001"
        }
    )


@app.post("/api/auth/logout")
async def logout():
    """User logout endpoint."""
    return BaseResponse(success=True, message="Başarıyla çıkış yapıldı")


# ============ Document Endpoints ============

@app.post("/api/documents/upload", response_model=DocumentResponse)
async def upload_document(
    file: UploadFile = File(...),
    background_tasks: BackgroundTasks = None
):
    """
    Upload a document for processing.
    Supports PDF, DOCX, and TXT files.
    """
    # Validate file type
    allowed_types = [
        "application/pdf",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "text/plain"
    ]
    allowed_extensions = [".pdf", ".docx", ".txt"]
    
    if file.content_type not in allowed_types:
        ext = "." + file.filename.split(".")[-1].lower() if "." in file.filename else ""
        if ext not in allowed_extensions:
            raise HTTPException(
                status_code=400,
                detail="Desteklenmeyen dosya türü. PDF, DOCX veya TXT yükleyin."
            )
    
    # Read file content
    content = await file.read()
    
    # Upload document
    result = await doc_service.upload_document(
        file_content=content,
        filename=file.filename,
        mime_type=file.content_type or "application/octet-stream",
        user_id="demo_user",  # In production, get from auth
        org_id="00000000-0000-0000-0000-000000000001"
    )
    
    if not result["success"]:
        raise HTTPException(status_code=500, detail=result.get("error", "Yükleme başarısız"))
    
    # Process document in background
    if background_tasks:
        background_tasks.add_task(process_document_task, result["document_id"])
    
    return DocumentResponse(
        success=True,
        message="Doküman yüklendi, işleniyor...",
        document=result.get("document")
    )


async def process_document_task(document_id: str):
    """Background task for document processing."""
    # Process document (extract text, create chunks)
    await doc_service.process_document(document_id)
    # Generate embeddings
    await embed_service.process_document_embeddings(document_id)


@app.get("/api/documents", response_model=DocumentListResponse)
async def list_documents():
    """Get all documents for the current organization."""
    documents = await doc_service.get_documents("00000000-0000-0000-0000-000000000001")
    return DocumentListResponse(
        success=True,
        documents=documents,
        total=len(documents)
    )


@app.delete("/api/documents/{document_id}")
async def delete_document(document_id: str):
    """Delete a document and all its chunks."""
    success = await doc_service.delete_document(document_id, "00000000-0000-0000-0000-000000000001")
    if not success:
        raise HTTPException(status_code=404, detail="Doküman bulunamadı")
    return BaseResponse(success=True, message="Doküman silindi")


# ============ Chat Endpoints ============

@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Send a message and get AI response with source citations.
    Uses RAG approach to find relevant document chunks.
    """
    result = await chat_service.chat_with_context(
        message=request.message,
        org_id="00000000-0000-0000-0000-000000000001",
        conversation_history=[msg.dict() for msg in request.conversation_history]
    )
    
    if not result["has_sources"]:
        return NoSourceResponse()
    
    return ChatResponse(
        success=True,
        answer=result["answer"],
        sources=result["sources"],
        has_sources=True
    )


@app.get("/api/chat/suggestions")
async def get_suggestions():
    """Get suggested questions based on indexed documents."""
    suggestions = await chat_service.get_suggested_questions("00000000-0000-0000-0000-000000000001")
    return {"suggestions": suggestions}


# ============ Dashboard Endpoints ============

@app.get("/api/dashboard/stats", response_model=DashboardStats)
async def get_dashboard_stats():
    """Get dashboard statistics from database."""
    stats = await db_service.get_dashboard_stats("00000000-0000-0000-0000-000000000001")
    return DashboardStats(**stats)


@app.get("/api/dashboard/recent-documents")
async def get_recent_documents():
    """Get recent documents."""
    documents = await db_service.get_recent_documents("00000000-0000-0000-0000-000000000001", limit=5)
    return {"documents": documents}


@app.get("/api/dashboard/recent-questions")
async def get_recent_questions():
    """Get recent chat questions."""
    questions = await db_service.get_recent_questions("00000000-0000-0000-0000-000000000001", limit=5)
    return {"questions": questions}


# ============ Run Application ============

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug
    )
