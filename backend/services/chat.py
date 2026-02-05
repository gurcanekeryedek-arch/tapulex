"""
Chat service.
Handles RAG-based chat with source citations.
"""

from typing import List, Dict, Any, Optional
from openai import OpenAI
from supabase import create_client, Client
from config import get_settings


def get_settings_fresh():
    return get_settings()

def get_supabase() -> Client:
    """Get Supabase client instance with service role key."""
    settings = get_settings_fresh()
    key = settings.supabase_service_key if settings.supabase_service_key else settings.supabase_key
    return create_client(settings.supabase_url, key)


SYSTEM_PROMPT = """Sen TapuLex, şirket dokümanlarından bilgi sağlayan yardımcı bir asistansın.

KURALLAR:
1. SADECE sağlanan bağlam (context) içindeki bilgilere dayanarak yanıt ver.
2. Eğer bağlamda yeterli bilgi YOKSA, açıkça "Bu bilgiyi yüklenen dokümanlarda bulamadım." de.
3. ASLA bağlamda olmayan bilgileri uydurma veya tahmin etme.
4. Her yanıtta kaynak göster (hangi doküman, hangi bölüm).
5. Yanıtlarını Türkçe ver.
6. Bilgiyi net ve düzenli bir şekilde sun.

FORMAT:
- Önemli bilgileri **kalın** yap
- Listeleme için madde işaretleri kullan
- Uzun yanıtları bölümlere ayır"""


async def search_chunks_by_text(query: str, org_id: str, limit: int = 5) -> List[Dict[str, Any]]:
    """
    Search for document chunks using text similarity.
    Supports basic keyword matching.
    """
    supabase = get_supabase()
    
    try:
        # Split query into words to search for keywords
        keywords = [word.strip() for word in query.split() if len(word.strip()) > 2]
        
        if not keywords:
            # Fallback to recent chunks if no keywords
            result = supabase.table("document_chunks")\
                .select("*, documents!inner(filename)")\
                .limit(limit)\
                .execute()
            return result.data or []

        # Try to find chunks containing any of the keywords
        # Supabase doesn't easily support multiple ILIKEs in one call with OR without custom SQL
        # So we'll just search for the first 2 keywords and combine
        
        all_matches = []
        for kw in keywords[:2]:
            result = supabase.table("document_chunks")\
                .select("*, documents!inner(filename)")\
                .ilike("text", f"%{kw}%")\
                .limit(limit)\
                .execute()
            if result.data:
                all_matches.extend(result.data)
        
        # Deduplicate matches by ID
        unique_matches = {m["id"]: m for m in all_matches}.values()
        
        chunks = list(unique_matches)[:limit]
        
        # If no matches found with keywords, return most recent
        if not chunks:
            result = supabase.table("document_chunks")\
                .select("*, documents!inner(filename)")\
                .limit(limit)\
                .execute()
            chunks = result.data or []
        
        # Add filename to metadata
        for chunk in chunks:
            if "documents" in chunk and chunk["documents"]:
                if "metadata" not in chunk or chunk["metadata"] is None:
                    chunk["metadata"] = {}
                chunk["metadata"]["filename"] = chunk["documents"].get("filename", "Bilinmeyen")
        
        return chunks
        
    except Exception as e:
        print(f"Search chunks error: {e}")
        return []


async def chat_with_context(
    message: str,
    org_id: str,
    conversation_history: List[Dict[str, str]] = None
) -> Dict[str, Any]:
    """
    Process a chat message using RAG approach.
    """
    settings = get_settings_fresh()
    openai_client = OpenAI(api_key=settings.openai_api_key)
    
    # Search for relevant chunks
    relevant_chunks = await search_chunks_by_text(
        query=message,
        org_id=org_id,
        limit=5
    )
    
    # If no relevant chunks found
    if not relevant_chunks:
        return {
            "answer": "Bu bilgiyi yüklenen dokümanlarda bulamadım. Lütfen farklı bir soru sorun veya ilgili dokümanları yükleyin.",
            "sources": [],
            "has_sources": False
        }
    
    # Build context from chunks
    context = build_context(relevant_chunks)
    
    # Build messages for LLM
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    
    # Add conversation history
    if conversation_history:
        for msg in conversation_history[-6:]:
            messages.append({"role": msg["role"], "content": msg["content"]})
    
    # Add current message with context
    user_message = f"BAĞLAM (Context):\n{context}\n\nSORU:\n{message}"
    messages.append({"role": "user", "content": user_message})
    
    try:
        response = openai_client.chat.completions.create(
            model=settings.chat_model,
            messages=messages,
            max_tokens=settings.max_tokens,
            temperature=settings.temperature
        )
        answer = response.choices[0].message.content
    except Exception as e:
        print(f"OpenAI error: {e}")
        answer = f"Bana sorduğunuz soruyu yanıtlamaya çalışırken bir hata oluştu: {str(e)}"
    
    # Build source citations
    sources = build_sources(relevant_chunks)
    
    return {
        "answer": answer,
        "sources": sources,
        "has_sources": True if sources else False
    }


def build_context(chunks: List[Dict[str, Any]]) -> str:
    context_parts = []
    for i, chunk in enumerate(chunks, 1):
        filename = (chunk.get("metadata") or {}).get("filename") or "Bilinmeyen"
        context_parts.append(f"[Kaynak {i}: {filename}]\n{chunk.get('text', '')}\n---")
    return "\n\n".join(context_parts)


def build_sources(chunks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    sources = []
    seen_ids = set()
    
    for chunk in chunks:
        doc_id = chunk.get("document_id")
        if doc_id in seen_ids:
            continue
        seen_ids.add(doc_id)
        
        metadata = chunk.get("metadata") or {}
        text = chunk.get("text", "")
        excerpt = text[:200] + "..." if len(text) > 200 else text
        
        sources.append({
            "document_id": doc_id,
            "filename": metadata.get("filename") or "Bilinmeyen",
            "page": metadata.get("page", 1),
            "section": metadata.get("section_title"),
            "excerpt": excerpt,
            "relevance_score": 0.9
        })
    return sources


async def get_suggested_questions(org_id: str) -> List[str]:
    return [
        "Yıllık izin hakları nedir?",
        "Evden çalışma politikası",
        "Performans değerlendirme süreci",
        "Yan haklar nelerdir?"
    ]
