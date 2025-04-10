from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from starlette.middleware.sessions import SessionMiddleware
from my_todo_app.auth.auth_routes import router as auth_router
from my_todo_app.todolists.todo_routes import router as todo_router
import os
from dotenv import load_dotenv

load_dotenv()

# ✅ 절대경로로 templates 디렉토리 지정
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATE_DIR = os.path.join(BASE_DIR, "templates")
templates = Jinja2Templates(directory=TEMPLATE_DIR)

app = FastAPI()
app.add_middleware(SessionMiddleware, secret_key=os.getenv("SESSION_SECRET_KEY"))
app.include_router(auth_router)
app.include_router(todo_router)

@app.get("/", response_class=HTMLResponse)
def read_root(request: Request):
    user = request.session.get("user")
    is_local = os.getenv("ENV", "prod") == "local"
    return templates.TemplateResponse(request, "index.html", {
        "request": request,
        "user": user,
        "is_local": is_local
    })

for route in app.routes:
    print(route.path)
