# modules/formatter.py

def format_email_node(state: dict) -> dict:
    """
    입력:
      state: {
        "user_id": "u001",  # 요청으로 온 사용자 ID
        "keyword_summaries": [
          {"keyword": ..., "summaries": [{"title", "link", "published", "author", "summary"}, ...]}
        ]
      }
    출력: {"user_id": "u001", "html": "<html>..."}
    """
    # 요청으로 받은 user_id를 가져옴
    user_id = state.get("user_id", "")

    # HTML 콘텐츠 생성
    html_parts = [
        "<html><body>"
    ]

    # 키워드별 요약 리스트 구성
    for entry in state.get("keyword_summaries", []):
        keyword = entry.get("keyword", "")
        html_parts.append(f"<h2>키워드: {keyword}</h2>")
        html_parts.append("<ul>")
        for doc in entry.get("summaries", []):
            # 요약 내용 내 줄바꿈문자는 <br>로 변환
            safe_summary = doc.get("summary", "").replace("\n", "<br>")
            html_parts.append(
                "<li>"
                f"<a href=\"{doc.get('link','')}\">{doc.get('title','')}</a> "
                f"({doc.get('published','')} by {doc.get('author','')})<br>"
                f"{safe_summary}"
                "</li>"
            )
        html_parts.append("</ul>")

    html_parts.append("</body></html>")
    html = "\n".join(html_parts)

    # user_id를 별도 field에 포함하여 반환
    return {"user_id": user_id, "mail": html}
