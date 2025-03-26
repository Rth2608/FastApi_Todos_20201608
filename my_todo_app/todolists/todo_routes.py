from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import JSONResponse
from todolists import todo_service  # 서비스 로직을 가져옴

router = APIRouter(prefix="/api/todos", tags=["ToDo"])

@router.get("/")
def get_todos(request: Request):
    todos = todo_service.load_user_todos(request)
    return JSONResponse(content=todos)

@router.post("/")
def save_todos(request: Request, new_todos: list):
    todo_service.save_user_todos(request, new_todos)
    return {"message": "저장 완료!"}
