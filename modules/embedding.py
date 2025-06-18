# modules/embedding.py
import os
import vertexai
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_google_vertexai import VertexAIEmbeddings
from google.cloud import aiplatform
from dotenv import load_dotenv
load_dotenv()

# 환경 설정
USE_VERTEX = os.getenv("USE_VERTEX", "True").lower() == "true"
PROJECT_ID = os.getenv("GOOGLE_PROJECT_ID")
LOCATION = os.getenv("GOOGLE_LOCATION", "us-central1")
print(f"GOOGLE_APPLICATION_CREDENTIALS is set to: {os.getenv('GOOGLE_APPLICATION_CREDENTIALS')}")
print(f"GOOGLE_PROJECT_ID is set to: {os.getenv('GOOGLE_PROJECT_ID')}")
print(f"File exists at path: {os.path.exists(os.getenv('GOOGLE_APPLICATION_CREDENTIALS'))}")


aiplatform.init(project=PROJECT_ID, location=LOCATION)


# Vertex AI 초기화 및 Embedder 설정
if USE_VERTEX:
    if not PROJECT_ID:
        raise ValueError("GOOGLE_PROJECT_ID environment variable is required when USE_VERTEX is true")
    vertexai.init(project=PROJECT_ID, location=LOCATION)
    embedder = VertexAIEmbeddings(
        project=PROJECT_ID,
        location=LOCATION,
        model_name="text-multilingual-embedding-002"
    )
else:
    embedder = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )


def get_embedding(text: str) -> list[float]:
    """
    단일 텍스트에 대한 임베딩을 반환합니다.
    """
    return embedder.embed_query(text)


def get_embeddings(texts: list[str]) -> list[list[float]]:
    """
    텍스트 리스트에 대한 임베딩을 반환합니다.
    """
    return embedder.embed_documents(texts)
