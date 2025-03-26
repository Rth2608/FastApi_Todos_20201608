from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse
from starlette.middleware.sessions import SessionMiddleware
from auth.routes import router as auth_router
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

# 현재 로그인한 사용자의 이메일 주소를 세션에서 추출하여, 그 사람만의 ToDo 저장용 파일 경로를 만들어줌
def get_todo_file(request: Request):
    user = request.session.get("user")  # request.session["user"]에서 로그인한 사용자 정보 가져옴
    if not user:    # 만약 로그인 안 되어 있다면 401 Unauthorized 에러 발생
        raise HTTPException(status_code=401, detail="로그인이 필요합니다")
    
    email = user["email"]
    return f"data/todo_{email}.json"    # 로그인한 사용자의 이메일을 기반으로 파일 경로 생성

# 로그인한 사용자에 맞는 개인 To-Do 목록을 불러오는 함수
def load_user_todos(request: Request):
    filepath = get_todo_file(request)
    if os.path.exists(filepath):
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

# 로그인한 사용자의 ToDo 리스트를 JSON 파일에 저장하는 함수
def save_user_todos(request: Request, todos: list):
    filepath = get_todo_file(request)
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(todos, f, indent=4)

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