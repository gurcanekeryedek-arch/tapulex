"""
Embedding service.
Generates and stores embeddings using OpenAI.
"""

from typing import List, Dict, Any, Optional
from openai import OpenAI
from supabase import create_client, Client
from config import get_settings
import numpy as np


settings = get_settings()
openai_client = OpenAI(api_key=settings.openai_api_key)


def get_supabase() -> Client:
    """Get Supabase client instance with service role key."""
    key = settings.supabase_service_key if settings.supabase_service_key else settings.supabase_key
    return create_client(settings.supabase_url, key)


async def generate_embedding(text: str) -> List[float]:
    """
    Generate embedding for a single text using OpenAI.
    """
    response = openai_client.embeddings.create(
        model=settings.embedding_model,
        input=text,
        dimensions=settings.embedding_dimensions
    )
    return response.data[0].embedding


async def generate_embeddings_batch(texts: List[str]) -> List[List[float]]:
    """
    Generate embeddings for multiple texts in a batch.
    """
    response = openai_client.embeddings.create(
        model=settings.embedding_model,
        input=texts,
        dimensions=settings.embedding_dimensions
    )
    return [item.embedding for item in response.data]


async def store_chunk_embedding(chunk_id: str, embedding: List[float]) -> bool:
    """
    Store embedding for a document chunk in Supabase.
    Uses pgvector for vector storage.
    """
    supabase = get_supabase()
    
    try:
        supabase.table("document_chunks").update({
            "embedding": embedding
        }).eq("id", chunk_id).execute()
        return True
    except Exception:
        return False


async def search_similar_chunks(
    query: str,
    org_id: str,
    limit: int = 5,
    threshold: float = 0.7
) -> List[Dict[str, Any]]:
    """
    Search for similar document chunks using vector similarity.
    Uses Supabase RPC function for pgvector similarity search.
    """
    supabase = get_supabase()
    
    # Generate embedding for query
    query_embedding = await generate_embedding(query)
    
    # Call Supabase RPC function for similarity search
    # This requires a custom function in Supabase
    result = supabase.rpc(
        "match_documents",
        {
            "query_embedding": query_embedding,
            "match_threshold": threshold,
            "match_count": limit,
            "filter_org_id": org_id
        }
    ).execute()
    
    return result.data or []


async def process_document_embeddings(document_id: str) -> Dict[str, Any]:
    """
    Generate and store embeddings for all chunks of a document.
    """
    supabase = get_supabase()
    
    try:
        # Get all chunks for this document
        chunks_result = supabase.table("document_chunks")\
            .select("id, text")\
            .eq("document_id", document_id)\
            .is_("embedding", "null")\
            .execute()
        
        chunks = chunks_result.data or []
        
        if not chunks:
            return {"success": True, "processed": 0}
        
        # Process in batches of 100
        batch_size = 100
        processed = 0
        
        for i in range(0, len(chunks), batch_size):
            batch = chunks[i:i + batch_size]
            texts = [chunk["text"] for chunk in batch]
            
            # Generate embeddings for batch
            embeddings = await generate_embeddings_batch(texts)
            
            # Store each embedding
            for chunk, embedding in zip(batch, embeddings):
                await store_chunk_embedding(chunk["id"], embedding)
                processed += 1
        
        return {
            "success": True,
            "processed": processed,
            "document_id": document_id
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


def cosine_similarity(vec1: List[float], vec2: List[float]) -> float:
    """
    Calculate cosine similarity between two vectors.
    """
    a = np.array(vec1)
    b = np.array(vec2)
    return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))
