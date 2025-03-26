from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from starlette.middleware.sessions import SessionMiddleware
from auth.routes import router as auth_router
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

# 세션 미들웨어
app.add_middleware(SessionMiddleware, secret_key=os.getenv("SECRET_KEY"))

# 라우터 등록
app.include_router(auth_router)

# 루트 페이지 렌더링
@app.get("/", response_class=HTMLResponse)
def read_root():
    with open("templates/index.html", "r", encoding="utf-8") as f:
        html = f.read()
    return HTMLResponse(content=html)

@app.get("/favicon.ico")
def favicon():
    return ""