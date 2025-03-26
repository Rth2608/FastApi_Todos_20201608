import os, json
from fastapi import Request, HTTPException

# 현재 로그인한 사용자의 이메일 주소를 세션에서 추출하여, 그 사람만의 ToDo 저장용 파일 경로를 만들어줌
def get_todo_file(request: Request):
    user = request.session.get("user")
    if not user:
        raise HTTPException(status_code=401, detail="로그인이 필요합니다")
    
    name = user["name"]
    os.makedirs("data", exist_ok=True)
    return f"data/todo_{name}.json"

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
