-- Enable pgvector extension
create extension if not exists vector;

-- Match documents function for similarity search
-- This function is called by the backend to find similar chunks
create or replace function match_documents (
  query_embedding vector(1536),
  match_threshold float,
  match_count int,
  filter_org_id uuid default null
)
returns table (
  id uuid,
  document_id uuid,
  text text,
  metadata jsonb,
  similarity float,
  filename text
)
language plpgsql
as $$
begin
  return query
  select
    dc.id,
    dc.document_id,
    dc.text,
    dc.metadata,
    1 - (dc.embedding <=> query_embedding) as similarity,
    d.filename
  from document_chunks dc
  join documents d on dc.document_id = d.id
  where 1 - (dc.embedding <=> query_embedding) > match_threshold
  and (filter_org_id is null or d.org_id = filter_org_id)
  order by dc.embedding <=> query_embedding
  limit match_count;
end;
$$;

-- Create chat feedback table
create table if not exists chat_feedback (
  id uuid default gen_random_uuid() primary key,
  session_id uuid references chat_sessions(id) on delete cascade,
  message_id uuid, -- Optional link to specific message
  score integer not null check (score >= 1 and score <= 5),
  comment text,
  created_at timestamp with time zone default timezone('utc'::text, now()) not null
);

-- RLS policies for feedback
alter table chat_feedback enable row level security;

create policy "Users can insert their own feedback"
  on chat_feedback for insert
  with check (true); -- In a real app, check user ownership

create policy "Users can view their own feedback"
  on chat_feedback for select
  using (true);
