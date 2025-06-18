# modules/summarizer.py
import os
import google.generativeai as genai # 'palm' 대신 'genai'로 변경하고, GenerativeModel 사용을 위해 준비
from google.generativeai.types import HarmCategory, HarmBlockThreshold # (선택 사항) 유해성 필터링 설정을 위해 추가

# 설정 및 API 키 로드
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# 여기에 ListModels로 확인한 정확한 Gemini 1.5 Flash 모델 이름을 입력합니다.
# 일반적으로는 "gemini-1.5-flash" 또는 "gemini-1.5-flash-001"과 같은 형태일 수 있습니다.
MODEL = os.getenv("GEMINI_MODEL", "gemini-1.5-flash") # 또는 "models/gemini-1.5-flash"

# 모델 초기화
model = genai.GenerativeModel(
    model_name=MODEL,
    safety_settings={
        HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
        HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
        HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
        HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
    }
)

# 프롬프트 파일 로드 함수
def load_prompt(filename: str) -> str:
    base = os.path.dirname(__file__)
    path = os.path.join(base, "..", "prompts", filename)
    with open(path, encoding="utf-8") as f:
        return f.read()

# 프롬프트 템플릿 사전 로드
_CHUNK_TMPL = load_prompt("chunk_summary.txt")

# 1단계: 키워드별 문서 단위 요약 노드
def chunk_summarizer_node(state: dict) -> dict:
    """
    입력: {"by_keyword":[{"keyword":..., "docs":[{title, link, published, author, content}, ...]}]}
    출력: {"keyword_summaries":[
                 {"keyword":..., "summaries":[{"title", "link", "published", "author", "summary"}, ...]}
            ]}
    """
    result = []
    for entry in state.get("by_keyword", []):
        kw = entry.get("keyword", "")
        summaries = []
        for doc in entry.get("docs", []):
            # 문서 전체를 한번에 요약
            prompt = _CHUNK_TMPL.replace("{text}", doc.get("content", ""))
            
            # --- 변경 시작 ---
            try:
                # model.generate_content 사용 (이전에 초기화된 model 객체 사용)
                resp = model.generate_content(prompt, generation_config={"temperature": 0.7})
                summary_text = resp.text # resp.result 대신 resp.text 사용
            except Exception as e:
                print(f"Error generating summary for doc: {doc.get('title', 'N/A')}, Error: {e}")
                summary_text = "요약 생성 중 오류가 발생했습니다." # 오류 발생 시 기본 메시지
            # --- 변경 끝 ---

            summaries.append({
                "title": doc.get("title", ""),
                "link": doc.get("link", ""),
                "published": doc.get("published", ""),
                "author": doc.get("author", ""),
                "summary": summary_text # 수정된 변수명 사용
            })
        result.append({"keyword": kw, "summaries": summaries})
    return {"user_id": state.get("user_id", ""), "keyword_summaries": result}
