# modules/merger.py
from collections import defaultdict

def group_by_article(state: dict) -> dict:
    grouped = defaultdict(list)
    for d in state["docs"]:
        grouped[d["id"]].append(d["text"])
    articles = [{"article_id": aid, "content": "\n".join(txts)} for aid, txts in grouped.items()]
    return {"articles": articles}
