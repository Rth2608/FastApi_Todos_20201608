from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from starlette.middleware.sessions import SessionMiddleware
from auth.auth_routes import router as auth_router
from todolists.todo_routes import router as todo_router
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()
templates = Jinja2Templates(directory="templates")

app.add_middleware(SessionMiddleware, secret_key=os.getenv("SESSION_SECRET_KEY"))
app.include_router(auth_router)
app.include_router(todo_router)

@app.get("/", response_class=HTMLResponse)
def read_root(request: Request):
    user = request.session.get("user")
    is_local = os.getenv("ENV", "prod") == "local"
    return templates.TemplateResponse("index.html", {
        "request": request,
        "user": user,
        "is_local": is_local
    })