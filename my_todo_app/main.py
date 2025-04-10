from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from starlette.middleware.sessions import SessionMiddleware
from my_todo_app.auth.auth_routes import router as auth_router
from my_todo_app.todolists.todo_routes import router as todo_router
import os
from dotenv import load_dotenv

# .env 파일 불러오기
load_dotenv()

# templates 디렉토리 경로 설정
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATE_DIR = os.path.join(BASE_DIR, "templates")
templates = Jinja2Templates(directory=TEMPLATE_DIR)

# FastAPI 앱 생성
app = FastAPI()

# 세션 미들웨어 추가 (비밀 키는 .env에서 가져옴)
app.add_middleware(SessionMiddleware, secret_key=os.getenv("SESSION_SECRET_KEY"))

# 라우터 등록
app.include_router(auth_router)
app.include_router(todo_router)

# 루트 페이지
@app.get("/", response_class=HTMLResponse)
def read_root(request: Request):
    user = request.session.get("user")
    is_local = os.getenv("ENV", "prod") == "local"
    return templates.TemplateResponse(request, "index.html", {
        "request": request,
        "user": user,
        "is_local": is_local
    })

# ✅ /register 페이지 라우트 추가 (테스트 대응용)
@app.get("/register", response_class=HTMLResponse)
def get_register_page(request: Request):
    return templates.TemplateResponse(request, "register.html", {"request": request})

# 디버깅용 라우트 확인 (실제 사용 시 삭제 가능)
for route in app.routes:
    print(f"📌 라우트 등록됨: {route.path}")
