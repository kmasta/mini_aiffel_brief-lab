# modules/retriever.py

import os
from modules.vector_store import similarity_search

def vector_retriever(state: dict) -> dict:
    """
    입력: state["keywords"], state["user_id"]
    - 키워드당 최고 5개 검색 → threshold 필터 → 중복(link) 제거 → 최대 3개
    반환: {"by_keyword": [...], "user_id": ...}
    """
    threshold = float(os.getenv("SIMILARITY_THRESHOLD", "0.6"))
    result = []
    for kw in state.get("keywords", []):
        raw_docs = similarity_search(kw, k=10, score_threshold=threshold)
        seen_links = set()
        unique_docs = []
        for d in raw_docs:
            link = d.metadata.get("link", "")
            if link and link in seen_links:
                print (f"Skip duplicated({ d.metadata.get('chunk_idx','')}/{d.metadata.get('total_chunks', '')}) link:{link}")
                continue

            seen_links.add(link)
            unique_docs.append({
                "title":     d.metadata.get("title", ""),
                "link":      link,
                "published": d.metadata.get("published", ""),
                "author":    d.metadata.get("author", ""),
                "summary":    d.metadata.get("summary", ""),
                "chunk_idx":    d.metadata.get("chunk_idx", ""),
                "total_chunks":    d.metadata.get("total_chunks", ""),
                "content":   d.page_content,
            })
            if len(unique_docs) >= 3:
                break

        result.append({
            "keyword": kw,
            "docs":     unique_docs
        })

    return {
        "by_keyword": result,
        "user_id":    state.get("user_id", "")
    }
