from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from starlette.middleware.sessions import SessionMiddleware
from my_todo_app.auth.auth_routes import router as auth_router
from my_todo_app.todolists.todo_routes import router as todo_router
import os
from prometheus_fastapi_instrumentator import Instrumentator
import logging
import time
from multiprocessing import Queue
from os import getenv
from logging_loki import LokiQueueHandler


# templates 디렉토리 경로 설정
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATE_DIR = os.path.join(BASE_DIR, "templates")
templates = Jinja2Templates(directory=TEMPLATE_DIR)

# FastAPI 앱 생성
app = FastAPI()
# Prometheus 메트릭스 엔드포인트 (/metrics)
Instrumentator().instrument(app).expose(app, endpoint="/metrics")
# 세션 미들웨어 추가
app.add_middleware(
    SessionMiddleware, secret_key=os.getenv("SESSION_SECRET_KEY", "dev-secret-key")
)

loki_logs_handler = LokiQueueHandler(
    Queue(-1),
    url=getenv("LOKI_ENDPOINT"),
    tags={"application": "fastapi"},
    version="1",
)

# Custom access logger (ignore Uvicorn's default logging)
custom_logger = logging.getLogger("custom.access")
custom_logger.setLevel(logging.INFO)

# Add Loki handler (assuming `loki_logs_handler` is correctly configured)
custom_logger.addHandler(loki_logs_handler)


async def log_requests(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    duration = time.time() - start_time  # Compute response time

    log_message = f'{request.client.host} - "{request.method} {request.url.path} HTTP/1.1" {response.status_code} {duration:.3f}s'

    # **Only log if duration exists**
    if duration:
        custom_logger.info(log_message)

    return response


app.middleware("http")(log_requests)

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
