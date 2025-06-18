# modules/vector_store.py
import os
from langchain_community.vectorstores import FAISS
from modules.embedding import embedder  # unified embedder from embedding.py

# FAISS index 저장 경로
INDEX_PATH = os.getenv("VECTOR_DB_PATH", "./data/vector_db")


def save_documents(docs):
    """
    문서 리스트로부터 FAISS 인덱스를 생성하고 로컬에 저장합니다.
    docs: List[langchain.Document]
    """
    # modules.embedding.embedder implements embed_documents and embed_query
    db = FAISS.from_documents(docs, embeddings=embedder)
    os.makedirs(INDEX_PATH, exist_ok=True)
    db.save_local(INDEX_PATH)


def load_db():
    """
    로컬에 저장된 FAISS 인덱스를 로드합니다.
    """
    return FAISS.load_local(
        INDEX_PATH,
        embeddings=embedder,
        allow_dangerous_deserialization=True
    )


def similarity_search(query: str, k: int = 5):
    """
    질의(query)에 대해 top-k 유사 문서를 반환합니다.
    """
    db = load_db()
    return db.similarity_search(query, k=k)

