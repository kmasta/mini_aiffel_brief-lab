# 뉴스 요약 서비스 프로젝트

아이펠 리서치 13기 brief-lab 팀의  미니 아이펠톤 프로젝트 
## 전체 시스템 개요

미니 아이펠톤 팀 프로젝트는 다음과 같은 컴포넌트로 구성되어 있습니다:

1. **뉴스 수집 서비스**

   * RSS 및 뉴스 API를 통해 최신 기사를 수집하고 데이터베이스에 저장
   * 별도의 백엔드로 독립 운영
2. **뉴스 요약 백엔드** (이 저장소)

   * 저장된 기사를 벡터 검색, LLM 기반 요약, HTML 이메일 포맷으로 변환
   * FastAPI + LangGraph로 구현
3. **n8n 워크플로우**

   * 일정에 따라 뉴스 수집 실행 
   * 요약 백엔드 호출 후 생성된 HTML을 받아 이메일 발송 처리
4. **요약 성능 테스트**

   * 다양한 프롬프트와 모델(Gemini, SBERT) 조합 비교 분석
   * 별도 테스트 스크립트로 성능 지표 수집 및 보고

---

## 이 저장소(뉴스 요약 백엔드) 역할

이 저장소는 **뉴스 요약 백엔드**에 해당하며 사용자가 설정한 키워드를 바탕으로 최신 뉴스 기사를 검색하고, 각 기사를 요약한 후 HTML 이메일 형태로 제공하는 백엔드 서비스입니다.    
주요 기능은 다음과 같습니다:

* **API 서버**: `/generate-summary` 엔드포인트로 사용자 요청 처리
* **파이프라인 정의**: LangGraph를 이용해 검색→요약→포맷 순으로 실행 ( node - file )
  * **벡터 검색** (retrieve - `modules/retriever.py`)
  
    * 벡터  `similarity_search` 기반 검색으로 키워드에 해당하는 뉴스 데이터 반환 
  
  * **문서 요약** (chunk_sum - `modules/summarizer.py`)
  
    * Google Gemini 또는 다른 모델 기반 LLM 호출로 기사 요약
  * **결과 포맷팅** (format - `modules/formatter.py`)
  
    * 키워드, 제목, 링크, 발행일, 작성자, 요약을 포함한 HTML 생성

```bash
# 백엔드 간단 실행 예시
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

이 저장소를 통해 생성된 HTML을 이메일 서비스에 연계하면, 사용자가 설정한 키워드 기반 맞춤형 뉴스 요약 메일 발송까지 완성됩니다.

---

## 디렉토리 구조

```bash
mini_aiffel_brief-lab/
├── app/
│   ├── __init__.py
│   ├── main.py                  # FastAPI + LangGraph API 서버
│   ├── router.py                # FastAPI 라우터 (POST /generate-summary 등)
│   ├── langgraph_builder.py     # LangGraph 파이프라인 정의
│   └── settings.py              # API 키, 설정값 로딩용
│
├── modules/
│   ├── retriever.py             # Vector DB 검색 (FAISS or Vertex)
│   ├── summarizer.py            # 청크 요약, 기사 요약, 메일 포맷 요약 등
│   ├── vector_store.py          # 벡터 저장/불러오기 함수
│   ├── splitter.py              # 문서 청크 분할 + 메타 추가 ( 옵션 )
│   ├── embedding.py             # Vertex AI or HuggingFace 임베딩 함수
│   ├── merger.py                # article_id 기준 청크 병합 처리 ( 옵션  )
│   └── formatter.py             # HTML 메일 포맷 변환
│
├── data/
│   ├── raw_news/               # 수집된 원본 뉴스 파일 (옵션)
│   └── vector_db/              # FAISS 또는 기타 벡터 저장소
│
├── prompts/
│   ├── chunk_summary.txt       # 청크 요약 프롬프트
│   ├── article_summary.txt     # 병합 요약 프롬프트 ( 옵션 )
│   ├── email_template.txt      # 메일 정리용 프롬프트 ( 옵션 )
│   └── keyword_query.txt       # 사용자 키워드 → 검색 쿼리 ( 옵션 )
│
├── requirements.txt
├── README.md
└── run_colab_server.py         # Colab등 클라우드 환경에서 API 서버 + ngrok 실행용
```

## 설치 및 실행

1. **환경 변수 설정** (루트에 `.env` 파일 생성)

   ```dotenv
   GOOGLE_API_KEY=your_google_api_key
   GOOGLE_PROJECT_ID=your_project_id
   GOOGLE_APPLICATION_CREDENTIALS=your_gcp_key_path
   GOOGLE_LOCATION=asia-northeast3
   USE_VERTEX=true        # Vertex AI 임베딩 사용 여부
   VECTOR_DB_PATH=./data/vector_db
   NGROK_AUTH_TOKEN=your_ngrok_token
   ```
2. **패키지 설치**

   ```bash
   pip install -r requirements.txt
   ```
3. **vector db 생성** (필요시에만 테스트용으로 VERTEX 사용한 vector db가 이미 기본 폴더에 저장되어 있음)

4. **서버 시작**

   ```bash
   # 로컬 환경에서 grok 없이 실행하는 경우 
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   # 클라우드나 로컬에서 grok 서비스를 사용하는 경우
   python run_colab_server.py
   ```

## API 사용 예시

```
POST /generate-summary
Content-Type: application/json

{
  "user_id": "u001",
  "keywords": ["금융", "배터리"],
  "email": "user@example.com"
}
```

응답 예시:

```json
{
  "user_id": "u001",
  "html": "<html>...\n키워드: 금융..."  
}
```
실제 테스트 실행 명령(curl 사용):
```bash
curl -X POST 127.0.0.1:8000/generate-summary  -H "Content-Type: application/json" -d '{"user_id": "u001","keywords": ["금융", "배터리"],"email": "user@example.com"}'
```

## 파이프라인 흐름

1. **retrieve**: 입력 키워드마다 FAISS에서 상위 5개 문서 검색
2. **summarizer**: 각 문서 전체를 LLM으로 요약
3. **formatter**: JSON 상태를 사용자 ID 포함 HTML 이메일로 포맷

## 모듈 설명

* **modules/embedding.py**: `USE_VERTEX` 설정에 따라 Vertex AI 또는 SBERT 임베딩 제공
* **modules/vector\_store.py**: FAISS 인덱스 생성, 저장, 로드, 검색 함수
* **modules/retriever.py**: 키워드 리스트를 받아 `similarity_search` 실행
* **modules/summarizer.py**: `chunk_summary.txt` 템플릿을 사용해 요약 수행
* **modules/formatter.py**: 결과를 HTML 형식으로 조합



