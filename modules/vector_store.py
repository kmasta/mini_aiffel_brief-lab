# modules/vector_store.py
import os
from langchain_community.vectorstores import FAISS
from modules.embedding import embedder  # unified embedder from embedding.py

# FAISS index 저장 경로
INDEX_PATH = os.getenv("VECTOR_DB_PATH", "./data/vector_db")

# NOT USED only for test
def save_documents(docs):
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

def similarity_search(query: str, k: int = 5, score_threshold: float = 0.0):
    """
    query 에 대해 top-k(fetch_k) 까지 검색한 뒤,
    score_threshold 이상인 문서만 반환합니다.
    - score_threshold: 유사도 임계값 (e.g. 0.7)
    """
    db = load_db()
    # fetch_k = k 로 설정해서 정확히 k개까지 점수 기록
    docs_and_scores = db.similarity_search_with_score(
        query, k=k, fetch_k=k
    )
    # score_threshold 이상인 것만 필터
    filtered = [
        doc for doc, score in docs_and_scores
        if score >= score_threshold
    ]
    return filtered
