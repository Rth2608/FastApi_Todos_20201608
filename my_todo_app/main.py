from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from starlette.middleware.sessions import SessionMiddleware
from auth.auth_routes import router as auth_router
from todolists.todo_routes import router as todo_router
import os
from dotenv import load_dotenv

load_dotenv()
templates = Jinja2Templates(directory="templates")

app = FastAPI()



# 세션 미들웨어
app.add_middleware(SessionMiddleware, secret_key=os.getenv("SECRET_KEY"))

# 라우터 등록
app.include_router(auth_router)
app.include_router(todo_router)

@app.get("/favicon.ico")
def favicon():
    return ""

@app.get("/", response_class=HTMLResponse)
def read_root(request: Request):
    user = request.session.get("user")
    return templates.TemplateResponse("index.html", {"request": request, "user": user})
