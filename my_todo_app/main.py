from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
import json
import os

app = FastAPI()

# To-Do 항목 모델
class TodoItem(BaseModel):
    id: int
    student_id: str  # 제목
    name: str  # 설명
    completed: bool = False

TODO_FILE = "todo.json"


def load_todos():
    if os.path.exists(TODO_FILE):
        with open(TODO_FILE, "r", encoding="utf-8") as file:    # 기존 파일인 todo.json을 읽기 모드("r")로 열어 UTF-8 인코딩으로 읽음
            todos = json.load(file)                             # json.load()는 JSON 데이터를 list[dict]로 변환하여 저장
        return todos
    return []

def save_todos(todos):
    with open(TODO_FILE, "w", encoding="utf-8") as file:    # 기존 파일인 todo.json을 덮어쓰기 모드("w")로 열어 UTF-8 인코딩으로 저장
        json.dump(todos, file, indent=4)                    # json.dump()는 todos를 JSON 형식으로 변환하여 파일에 저장하며 indent=4는는 JSON 데이터를 들여쓰기 4칸으로 포맷팅하여 가독성을 높임

@app.get("/todos", response_model=list[TodoItem])
def get_todos():
    todos = load_todos()
    print("get_todos():", todos)
    return todos

@app.post("/todos", response_model=TodoItem)
def create_todo(todo: TodoItem):    # 클라이언트가 보낸 새로운 To-Do 데이터를 TodoItem 모델로 받음
    todos = load_todos()
    todos.append(todo.model_dump()) # .model_dump(): todo를 dict로 변환
    save_todos(todos)
    return todo

@app.get("/todos/{todo_id}", response_model=TodoItem)
def get_todo(todo_id: int): # 매개변수로 To-Do 항목의 ID를 입력받음
    todos = load_todos()
    for todo in todos:
        if todo["id"] == todo_id:
            return todo
    raise HTTPException(status_code=404, detail="To-Do item not found")

@app.put("/todos/{todo_id}", response_model=TodoItem)
def update_todo(todo_id: int, updated_todo: TodoItem):  # todo_id: int는 수정할 To-Do 항목의 ID, updated_todo: TodoItem는 클라이언트가 보낸 새로운 데이터(TodoItem 모델)
    todos = load_todos()
    for todo in todos:
        if todo["id"] == todo_id:
            todo["student_id"] = updated_todo.student_id
            todo["name"] = updated_todo.name
            todo["completed"] = updated_todo.completed
            save_todos(todos)
            return todo
    raise HTTPException(status_code=404, detail="To-Do item not found")

@app.delete("/todos/{todo_id}", response_model=dict)    # todo_id: int는 삭제할 To-Do 항목의 ID
def delete_todo(todo_id: int):
    todos = load_todos()
    todos = [todo for todo in todos if todo["id"] != todo_id]
    save_todos(todos)
    return {"delete_todo(todo_id: " + todo_id + ")"}

@app.get("/", response_class=HTMLResponse)
def read_root():
    with open("templates/index.html", "r", encoding="utf-8") as file:
        content = file.read()               # file.read()는 HTML 파일의 내용을 문자열로 읽어 content 변수에 저장
    return HTMLResponse(content=content)    # FastAPI의 HTMLResponse 객체를 사용하여 index.html의 내용을 HTTP 응답으로 반환하며 클라이언트(웹 브라우저)는 HTML을 받아 웹 페이지로 렌더링

@app.get("/todos/student/{student_id}", response_model=list[TodoItem])
def get_todos_by_student(student_id: str):
    todos = load_todos()
    student_todos = [todo for todo in todos if todo["student_id"] == student_id]
    return student_todos