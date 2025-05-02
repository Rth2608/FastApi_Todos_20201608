from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
import os, json

router = APIRouter()

def get_user_file(user):
    os.makedirs("todos", exist_ok=True)
    return f"todos/{user['student_id']}_{user['name']}.json"

@router.get("/todos")
async def get_todos(request: Request):
    user = request.session.get("user")
    if not user:
        return JSONResponse(status_code=401, content={"error": "로그인이 필요합니다."})

    filepath = get_user_file(user)
    if not os.path.exists(filepath):
        return JSONResponse(content=[])

    with open(filepath, "r", encoding="utf-8") as f:
        todos = json.load(f)
    return JSONResponse(content=todos)

@router.post("/todos")
async def save_todos(request: Request):
    user = request.session.get("user")
    if not user:
        return JSONResponse(status_code=401, content={"error": "로그인이 필요합니다."})

    todos = await request.json()
    filepath = get_user_file(user)
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(todos, f, indent=4, ensure_ascii=False)
    return JSONResponse(content={"message": "저장 완료"})