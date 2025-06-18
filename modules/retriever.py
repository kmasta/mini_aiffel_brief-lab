# modules/retriever.py
from modules.vector_store import similarity_search

def vector_retriever(state: dict) -> dict:
    """
    입력: {"user_id":..., "keywords": [...], ...}
    출력: {"by_keyword": [
               {"keyword": "금융", "docs": [Document,...]},
               ...
           ]}
    """
    result = []
    for kw in state.get("keywords", []):
        docs = similarity_search(kw, k=5)
        # doc.metadata['title'] 등이 필요하다면 metadata에 포함되어야 함
        result.append({
            "keyword": kw,
            "docs": [
                {# TODO "id": d.metadata.get("article_id",""),
                 "title": d.metadata.get("title",""),
                 "link" : d.metadata.get("link",""),
                 "published" : d.metadata.get("published",""),
                 "author" : d.metadata.get("author",""),
                 "content": d.page_content}
                for d in docs
            ]
        })
    return {"user_id": state["user_id"], "by_keyword": result}