from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from starlette.middleware.sessions import SessionMiddleware
from my_todo_app.auth.auth_routes import router as auth_router
from my_todo_app.todolists.todo_routes import router as todo_router
import os
from prometheus_fastapi_instrumentator import Instrumentator

# Prometheus 메트릭스 엔드포인트 (/metrics)
Instrumentator().instrument(app).expose(app, endpoint="/metrics")
# templates 디렉토리 경로 설정
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATE_DIR = os.path.join(BASE_DIR, "templates")
templates = Jinja2Templates(directory=TEMPLATE_DIR)

# FastAPI 앱 생성
app = FastAPI()

# 세션 미들웨어 추가
app.add_middleware(
    SessionMiddleware, secret_key=os.getenv("SESSION_SECRET_KEY", "dev-secret-key")
)

# 라우터 등록
app.include_router(auth_router)
app.include_router(todo_router, prefix="/api")


# 루트 페이지
@app.get("/", response_class=HTMLResponse)
def read_root(request: Request):
    user = request.session.get("user")
    return templates.TemplateResponse("index.html", {"request": request, "user": user})


# 디버깅용 라우트 출력
for route in app.routes:
    print(f"📌 라우트 등록됨: {route.path}")
