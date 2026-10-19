import os
# 
from sqlalchemy import create_engine, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
# 
from dotenv import load_dotenv
# 

load_dotenv()

DATABASE_URL = os.getenv('DATABASE_URL')

if not DATABASE_URL:
    raise ValueError("DATABASE_URL not found...")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autoflush = False, autocommit = False, bind = engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_similarity(db, embed_input, k = 5) -> tuple:
    # print(embed_input)
    if isinstance(embed_input[0], list):
        embed_input = embed_input[0]
    
    embedding_str = "[" + ",".join(map(str, embed_input)) + "]"

    result = db.execute(text("""
    SELECT id, info, classification, disease,
           1 - (embedding <=> CAST(:embedding AS vector)) AS similarity
    FROM documents
    ORDER BY embedding <=> CAST(:embedding AS vector)
    LIMIT :top_k
"""), {"embedding": embedding_str, "top_k": k})

    return result.fetchall()
