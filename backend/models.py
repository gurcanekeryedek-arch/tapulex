from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum
import uuid


# Enums
class DocumentStatus(str, Enum):
    UPLOADED = "uploaded"
    PROCESSING = "processing"
    INDEXED = "indexed"
    FAILED = "failed"


class UserRole(str, Enum):
    ADMIN = "admin"
    MEMBER = "member"


# Base Models
class BaseResponse(BaseModel):
    success: bool = True
    message: Optional[str] = None


# Auth Models
class LoginRequest(BaseModel):
    email: str
    password: str


class LoginResponse(BaseResponse):
    access_token: str
    token_type: str = "bearer"
    user: Optional[Dict[str, Any]] = None


class UserProfile(BaseModel):
    id: str
    email: str
    full_name: Optional[str] = None
    org_id: Optional[str] = None
    role: UserRole = UserRole.MEMBER


# Organization Models
class Organization(BaseModel):
    id: str
    name: str
    created_at: datetime


# Document Models
class DocumentCreate(BaseModel):
    filename: str
    mime_type: str
    size_bytes: int


class Document(BaseModel):
    id: str
    org_id: str
    uploaded_by: Optional[str] = None
    storage_path: str
    filename: str
    mime_type: str
    size_bytes: int
    status: str = "uploaded"
    error_message: Optional[str] = None
    created_at: Optional[str] = None
    chunk_count: int = 0


class DocumentResponse(BaseResponse):
    document: Optional[Document] = None


class DocumentListResponse(BaseResponse):
    documents: List[Document] = []
    total: int = 0


# Chunk Models
class ChunkMetadata(BaseModel):
    page: Optional[int] = None
    section_title: Optional[str] = None
    char_start: int
    char_end: int


class DocumentChunk(BaseModel):
    id: str
    document_id: str
    chunk_index: int
    text: str
    metadata: ChunkMetadata


# Chat Models
class ChatMessage(BaseModel):
    role: str  # "user" or "assistant"
    content: str


class ChatRequest(BaseModel):
    message: str
    conversation_history: List[ChatMessage] = []


class SourceReference(BaseModel):
    document_id: str
    filename: str
    page: Optional[int] = None
    section: Optional[str] = None
    excerpt: str
    relevance_score: float


class ChatResponse(BaseResponse):
    answer: str
    sources: List[SourceReference] = []
    has_sources: bool = True


class NoSourceResponse(BaseResponse):
    answer: str = "Bu bilgiyi yüklenen dokümanlarda bulamadım."
    sources: List[SourceReference] = []
    has_sources: bool = False


# Stats Models
class DashboardStats(BaseModel):
    total_documents: int = 0
    total_chats: int = 0
    total_chunks: int = 0
    accuracy_rate: float = 98.5
    documents_this_week: int = 0
    chats_today: int = 0


class FeedbackRequest(BaseModel):
    session_id: str
    score: int = Field(..., ge=1, le=5)
    comment: Optional[str] = None
