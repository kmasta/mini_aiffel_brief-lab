# modules/summarizer.py
import os
import time
import google.generativeai as genai # 'palm' 대신 'genai'로 변경하고, GenerativeModel 사용을 위해 준비
from google.generativeai.types import HarmCategory, HarmBlockThreshold # (선택 사항) 유해성 필터링 설정을 위해 추가
from modules.splitter import chunk_text

# 설정 및 API 키 로드
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
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
CHUNK_TEMPLATE = load_prompt("chunk_summary.txt")


def safe_generate(prompt: str, retries: int = 3) -> str:
    for i in range(retries):
        try:
            resp = model.generate_content(prompt, generation_config={"temperature": 0.7})
            return resp.text
        except Exception as e:
            delay = getattr(e, 'retry_delay', None)
            sleep_sec = delay.seconds if delay and hasattr(delay, 'seconds') else 5 * (i + 1)
            time.sleep(sleep_sec)
    return "요약을 생성할 수 없습니다."

def chunk_summarizer_node(state: dict) -> dict:
    keyword_summaries = []
    for entry in state.get("by_keyword", []):
        kw = entry.get("keyword", "")
        summaries = []
        for doc in entry.get("docs", []):
            prompt = CHUNK_TEMPLATE.replace("{text}", doc.get("content", ""))
            summary_text = safe_generate(prompt)
            summaries.append({
                "title":     doc.get("title", ""),
                "link":      doc.get("link", ""),
                "published": doc.get("published", ""),
                "author":    doc.get("author", ""),
                "summary":   summary_text,
            })
        keyword_summaries.append({
            "keyword":   kw,
            "summaries": summaries
        })
    return {
        "keyword_summaries": keyword_summaries,
        "user_id":           state.get("user_id", "")
    }
