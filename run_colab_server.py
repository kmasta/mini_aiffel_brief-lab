# run_colab_server.py
import nest_asyncio
from pyngrok import ngrok
import uvicorn
from app.main import app
from dotenv import load_dotenv
import os

# 환경변수 로드
load_dotenv()

# ngrok 설정
ngrok.set_auth_token(os.getenv("NGROK_AUTH_TOKEN"))
public_url = ngrok.connect(8000).public_url
print(f"▶️ Public URL: {public_url}")

# Colab 이벤트 루프 충돌 방지
nest_asyncio.apply()

# 서버 실행
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
