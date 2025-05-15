import os, json
from fastapi import APIRouter, Request, Form
from fastapi.responses import RedirectResponse, JSONResponse
from fastapi.templating import Jinja2Templates

router = APIRouter()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATE_DIR = os.path.join(BASE_DIR, "..", "templates")
LOGIN_FILE = os.path.join(BASE_DIR, "..", "login_data", "login.json")
templates = Jinja2Templates(directory=TEMPLATE_DIR)

REGISTER_TEMPLATE = "register.html"
LOGIN_TEMPLATE = "login.html"


def load_users():
    if not os.path.exists(LOGIN_FILE):
        return []
    with open(LOGIN_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


@router.get("/register")
async def register(request: Request):
    return templates.TemplateResponse(REGISTER_TEMPLATE, {"request": request})


@router.get("/check-student-id")
async def check_student_id(student_id: str):
    users = load_users()
    for user in users:
        if str(user.get("student_id")) == str(student_id):
            return JSONResponse(content={"exists": True})
    return JSONResponse(content={"exists": False})


@router.post("/register/submit")
async def register_submit(
    request: Request,
    student_id: str = Form(...),
    name: str = Form(...),
    password: str = Form(...),
):
    users = load_users()
    for user in users:
        if str(user.get("student_id")) == str(student_id):
            return templates.TemplateResponse(
                REGISTER_TEMPLATE,
                {
                    "request": request,
                    "error": "이미 존재하는 학번입니다. 다른 학번으로 시도해주세요.",
                },
            )

    users.append(
        {
            "student_id": student_id,
            "name": name,
            "password": password,
        }
    )

    os.makedirs(os.path.dirname(LOGIN_FILE), exist_ok=True)
    with open(LOGIN_FILE, "w", encoding="utf-8") as f:
        json.dump(users, f, indent=4, ensure_ascii=False)

    request.session["user"] = {"student_id": student_id, "name": name}
    return RedirectResponse("/", status_code=302)


@router.get("/login")
async def login_form(request: Request):
    return templates.TemplateResponse(LOGIN_TEMPLATE, {"request": request})


@router.post("/login")
async def login(
    request: Request, student_id: str = Form(...), password: str = Form(...)
):
    users = load_users()
    for user in users:
        if str(user.get("student_id")) == str(student_id):
            if user.get("password") == password:
                request.session["user"] = user
                return RedirectResponse("/", status_code=302)
            else:
                return templates.TemplateResponse(
                    LOGIN_TEMPLATE,
                    {"request": request, "error": "비밀번호가 틀렸습니다."},
                )
    return templates.TemplateResponse(
        LOGIN_TEMPLATE,
        {"request": request, "error": "등록되지 않은 학번입니다."},
    )


@router.get("/logout")
def logout(request: Request):
    request.session.clear()
    return RedirectResponse("/", status_code=302)


@router.get("/withdraw")
async def withdraw(request: Request):
    user = request.session.get("user")
    if not user:
        return RedirectResponse("/", status_code=302)

    student_id = user.get("student_id")
    name = user.get("name")

    try:
        users = [
            u
            for u in load_users()
            if not (u.get("student_id") == student_id and u.get("name") == name)
        ]
        with open(LOGIN_FILE, "w", encoding="utf-8") as f:
            json.dump(users, f, indent=4, ensure_ascii=False)

        todo_path = f"todos/{student_id}_{name}.json"
        if os.path.exists(todo_path):
            os.remove(todo_path)

        request.session.clear()
        return RedirectResponse("/", status_code=302)

    except Exception as e:
        print(f"탈퇴 중 오류: {e}")
        return JSONResponse(status_code=500, content={"error": "탈퇴 중 오류 발생"})
