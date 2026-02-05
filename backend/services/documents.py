"""
Document processing service.
Handles document upload, parsing, and storage.
"""

from typing import Optional, List, Dict, Any
from supabase import create_client, Client
from config import get_settings
from utils.chunker import split_into_chunks
import uuid
import io
import os
import PyPDF2
from docx import Document as DocxDocument


settings = get_settings()

# Local storage path for development
LOCAL_STORAGE_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "uploads")
os.makedirs(LOCAL_STORAGE_PATH, exist_ok=True)


def get_supabase() -> Client:
    """Get Supabase client instance with service role key."""
    # Use service key to bypass RLS for admin operations
    key = settings.supabase_service_key if settings.supabase_service_key else settings.supabase_key
    return create_client(settings.supabase_url, key)


async def upload_document(
    file_content: bytes,
    filename: str,
    mime_type: str,
    user_id: str,
    org_id: str
) -> Dict[str, Any]:
    """
    Upload a document and create database record.
    Uses local storage for development, Supabase Storage for production.
    """
    supabase = get_supabase()
    doc_id = str(uuid.uuid4())
    storage_path = f"{org_id}/{doc_id}/{filename}"
    
    try:
        # Try Supabase Storage first
        try:
            supabase.storage.from_("docs").upload(
                storage_path,
                file_content,
                {"content-type": mime_type}
            )
        except Exception as storage_error:
            # Fallback to local storage
            print(f"Using local storage: {storage_error}")
            local_dir = os.path.join(LOCAL_STORAGE_PATH, org_id, doc_id)
            os.makedirs(local_dir, exist_ok=True)
            with open(os.path.join(local_dir, filename), "wb") as f:
                f.write(file_content)
        
        # Ensure org exists
        try:
            supabase.table("orgs").upsert({
                "id": org_id,
                "name": "Demo Organization"
            }).execute()
        except:
            pass
        
        # Create database record
        doc_data = {
            "id": doc_id,
            "org_id": org_id,
            "storage_bucket": "docs",
            "storage_path": storage_path,
            "filename": filename,
            "mime_type": mime_type,
            "size_bytes": len(file_content),
            "status": "uploaded"
        }
        
        result = supabase.table("documents").insert(doc_data).execute()
        
        # Extract and store text immediately (sync mode for simplicity)
        text = extract_text(file_content, mime_type, filename)
        if text:
            chunks = split_into_chunks(
                text,
                chunk_size=settings.chunk_size,
                chunk_overlap=settings.chunk_overlap
            )
            
            # Store chunks
            for chunk in chunks:
                chunk_data = {
                    "id": str(uuid.uuid4()),
                    "org_id": org_id,
                    "document_id": doc_id,
                    "chunk_index": chunk["chunk_index"],
                    "text": chunk["text"],
                    "metadata": {
                        "char_start": chunk["char_start"],
                        "char_end": chunk["char_end"],
                        "filename": filename
                    }
                }
                supabase.table("document_chunks").insert(chunk_data).execute()
            
            # Update status to indexed
            supabase.table("documents").update({
                "status": "indexed"
            }).eq("id", doc_id).execute()
        
        return {
            "success": True,
            "document_id": doc_id,
            "document": result.data[0] if result.data else doc_data
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


async def process_document(document_id: str) -> Dict[str, Any]:
    """
    Process a document: extract text, create chunks, generate embeddings.
    """
    supabase = get_supabase()
    
    try:
        # Update status to processing
        supabase.table("documents").update({
            "status": "processing"
        }).eq("id", document_id).execute()
        
        # Get document info
        doc_result = supabase.table("documents").select("*").eq("id", document_id).single().execute()
        doc = doc_result.data
        
        # Try to download file from storage
        try:
            file_data = supabase.storage.from_("docs").download(doc["storage_path"])
        except:
            # Try local storage
            parts = doc["storage_path"].split("/")
            local_path = os.path.join(LOCAL_STORAGE_PATH, *parts)
            with open(local_path, "rb") as f:
                file_data = f.read()
        
        # Extract text based on mime type
        text = extract_text(file_data, doc["mime_type"], doc["filename"])
        
        if not text:
            raise Exception("Could not extract text from document")
        
        # Split into chunks
        chunks = split_into_chunks(
            text,
            chunk_size=settings.chunk_size,
            chunk_overlap=settings.chunk_overlap,
            metadata={"document_id": document_id, "filename": doc["filename"]}
        )
        
        # Store chunks (embeddings will be generated separately)
        for chunk in chunks:
            chunk_data = {
                "id": str(uuid.uuid4()),
                "org_id": doc["org_id"],
                "document_id": document_id,
                "chunk_index": chunk["chunk_index"],
                "text": chunk["text"],
                "metadata": {
                    "char_start": chunk["char_start"],
                    "char_end": chunk["char_end"],
                    "filename": doc["filename"]
                }
            }
            supabase.table("document_chunks").insert(chunk_data).execute()
        
        # Update document status
        supabase.table("documents").update({
            "status": "indexed"
        }).eq("id", document_id).execute()
        
        return {
            "success": True,
            "document_id": document_id,
            "chunks_created": len(chunks)
        }
        
    except Exception as e:
        # Update status to failed
        supabase.table("documents").update({
            "status": "failed",
            "error_message": str(e)
        }).eq("id", document_id).execute()
        
        return {
            "success": False,
            "error": str(e)
        }


def extract_text(file_data: bytes, mime_type: str, filename: str) -> str:
    """
    Extract text from various document formats.
    """
    if mime_type == "application/pdf" or filename.endswith(".pdf"):
        return extract_pdf_text(file_data)
    elif mime_type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document" or filename.endswith(".docx"):
        return extract_docx_text(file_data)
    elif mime_type == "text/plain" or filename.endswith(".txt"):
        return file_data.decode("utf-8", errors="ignore")
    else:
        # Try to decode as text
        return file_data.decode("utf-8", errors="ignore")


def extract_pdf_text(file_data: bytes) -> str:
    """Extract text from PDF file."""
    text_parts = []
    
    try:
        pdf_reader = PyPDF2.PdfReader(io.BytesIO(file_data))
        
        for page_num, page in enumerate(pdf_reader.pages):
            page_text = page.extract_text()
            if page_text:
                text_parts.append(f"[Sayfa {page_num + 1}]\n{page_text}")
                
    except Exception as e:
        raise Exception(f"PDF parsing error: {str(e)}")
    
    return "\n\n".join(text_parts)


def extract_docx_text(file_data: bytes) -> str:
    """Extract text from DOCX file."""
    try:
        doc = DocxDocument(io.BytesIO(file_data))
        paragraphs = [para.text for para in doc.paragraphs if para.text.strip()]
        return "\n\n".join(paragraphs)
    except Exception as e:
        raise Exception(f"DOCX parsing error: {str(e)}")


async def get_documents(org_id: str) -> List[Dict[str, Any]]:
    """Get all documents for an organization."""
    supabase = get_supabase()
    
    try:
        result = supabase.table("documents")\
            .select("*")\
            .order("created_at", desc=True)\
            .execute()
        
        return result.data or []
    except Exception as e:
        print(f"Get documents error: {e}")
        return []


async def delete_document(document_id: str, org_id: str) -> bool:
    """Delete a document and its chunks."""
    supabase = get_supabase()
    
    try:
        # Get document info for storage path
        doc_result = supabase.table("documents").select("storage_path").eq("id", document_id).single().execute()
        
        if doc_result.data:
            # Try delete from storage
            try:
                supabase.storage.from_("docs").remove([doc_result.data["storage_path"]])
            except:
                pass
        
        # Delete chunks first (foreign key constraint)
        supabase.table("document_chunks").delete().eq("document_id", document_id).execute()
        
        # Delete document
        supabase.table("documents").delete().eq("id", document_id).execute()
        
        return True
    except Exception as e:
        print(f"Delete document error: {e}")
        return False
