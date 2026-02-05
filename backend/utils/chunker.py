"""
Text chunking utilities for document processing.
Splits documents into overlapping chunks for embedding.
"""

from typing import List, Dict, Any, Optional
import re


def split_into_chunks(
    text: str,
    chunk_size: int = 1000,
    chunk_overlap: int = 200,
    metadata: Optional[Dict[str, Any]] = None
) -> List[Dict[str, Any]]:
    """
    Split text into overlapping chunks.
    
    Args:
        text: The text to split
        chunk_size: Target size for each chunk (in characters)
        chunk_overlap: Overlap between consecutive chunks
        metadata: Optional metadata to attach to each chunk
        
    Returns:
        List of chunk dictionaries with text and metadata
    """
    if not text or not text.strip():
        return []
    
    # Clean the text
    text = clean_text(text)
    
    # Split by paragraphs first
    paragraphs = re.split(r'\n\s*\n', text)
    
    chunks = []
    current_chunk = ""
    current_start = 0
    char_position = 0
    
    for para in paragraphs:
        para = para.strip()
        if not para:
            continue
            
        # If adding this paragraph would exceed chunk_size
        if len(current_chunk) + len(para) + 1 > chunk_size and current_chunk:
            # Save current chunk
            chunks.append({
                "text": current_chunk.strip(),
                "char_start": current_start,
                "char_end": char_position,
                "chunk_index": len(chunks)
            })
            
            # Start new chunk with overlap
            overlap_start = max(0, len(current_chunk) - chunk_overlap)
            current_chunk = current_chunk[overlap_start:] + "\n\n" + para
            current_start = char_position - (len(current_chunk) - len(para) - 2)
        else:
            if current_chunk:
                current_chunk += "\n\n"
            current_chunk += para
            
        char_position += len(para) + 2  # +2 for paragraph separator
    
    # Don't forget the last chunk
    if current_chunk.strip():
        chunks.append({
            "text": current_chunk.strip(),
            "char_start": current_start,
            "char_end": char_position,
            "chunk_index": len(chunks)
        })
    
    # Add metadata to each chunk
    if metadata:
        for chunk in chunks:
            chunk["metadata"] = {**metadata, **chunk}
    
    return chunks


def clean_text(text: str) -> str:
    """Clean and normalize text."""
    # Remove excessive whitespace
    text = re.sub(r'\s+', ' ', text)
    # Remove special characters that might cause issues
    text = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\x9f]', '', text)
    # Normalize line breaks
    text = re.sub(r'\r\n', '\n', text)
    text = re.sub(r'\r', '\n', text)
    # Remove multiple newlines but keep paragraph structure
    text = re.sub(r'\n{3,}', '\n\n', text)
    return text.strip()


def extract_sections(text: str) -> List[Dict[str, str]]:
    """
    Extract sections from text based on headers.
    Useful for preserving document structure.
    """
    # Common header patterns
    header_pattern = r'^(?:#{1,6}\s+|[A-Z][A-Za-z\s]+:|\d+\.\s+[A-Z])'
    
    lines = text.split('\n')
    sections = []
    current_section = {"title": "Introduction", "content": ""}
    
    for line in lines:
        if re.match(header_pattern, line.strip()):
            if current_section["content"].strip():
                sections.append(current_section)
            current_section = {
                "title": line.strip().lstrip('#').strip(),
                "content": ""
            }
        else:
            current_section["content"] += line + "\n"
    
    if current_section["content"].strip():
        sections.append(current_section)
    
    return sections


def estimate_tokens(text: str) -> int:
    """
    Estimate token count for a given text.
    Rough estimate: ~4 characters per token for English.
    """
    return len(text) // 4
