import os, json
from fastapi import APIRouter, Request, Form
from fastapi.responses import RedirectResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from authlib.integrations.starlette_client import OAuth
from starlette.config import Config

router = APIRouter()
templates = Jinja2Templates(directory="templates")

USE_GOOGLE_AUTH = os.getenv("USE_GOOGLE_AUTH", "False").lower() == "true"

if USE_GOOGLE_AUTH:
    config = Config(".env")
    oauth = OAuth(config)
    oauth.register(
        name='google',
        client_id=config("GOOGLE_CLIENT_ID"),
        client_secret=config("GOOGLE_CLIENT_SECRET"),
        server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
        client_kwargs={'scope': 'openid email profile'}
    )

LOGIN_FILE = "login_data/login.json"

def load_users():
    if not os.path.exists(LOGIN_FILE):
        return []
    with open(LOGIN_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_user(student_id, name):
    users = load_users()
    for u in users:
        if u["student_id"] == student_id and u["name"] == name:
            return  # 중복 방지
    users.append({"student_id": student_id, "name": name})
    os.makedirs("login_data", exist_ok=True)
    with open(LOGIN_FILE, "w", encoding="utf-8") as f:
        json.dump(users, f, indent=4, ensure_ascii=False)

if USE_GOOGLE_AUTH:

    @router.get("/register")
    async def register(request: Request):
        redirect_uri = request.url_for("auth_callback")
        return await oauth.google.authorize_redirect(request, redirect_uri)

    @router.get("/auth/callback")
    async def auth_callback(request: Request):
        token = await oauth.google.authorize_access_token(request)
        user_info = await oauth.google.get("https://openidconnect.googleapis.com/v1/userinfo", token=token)
        user_info = user_info.json()

        google_id = user_info.get("sub") or user_info.get("id")

        if not google_id:
            return JSONResponse(status_code=400, content={"error": "구글 사용자 식별값이 없습니다."})

        # 중복 가입 확인
        users = load_users()
        for user in users:
            if user.get("id") == google_id:
                return templates.TemplateResponse("register.html", {
                    "request": request,
                    "name": "사용자",
                    "error": "이미 이 계정으로 가입된 사용자가 존재합니다."
                })

        request.session["temp_user"] = {"id": google_id}

        return templates.TemplateResponse("register.html", {"request": request})

@router.post("/register/submit")
async def register_submit(
    request: Request,
    student_id: str = Form(...),
    name: str = Form(...)
):
    temp_user = request.session.pop("temp_user", None)
    if not temp_user or "id" not in temp_user:
        return RedirectResponse("/", status_code=302)

    google_id = temp_user["id"]

    users = load_users()
    for user in users:
        if user["student_id"] == student_id:
            return templates.TemplateResponse("register.html", {
                "request": request,
                "error": "이미 존재하는 학번입니다. 다른 학번으로 시도해주세요."
            })

    users.append({"student_id": student_id, "name": name, "id": google_id})

    os.makedirs("login_data", exist_ok=True)
    with open(LOGIN_FILE, "w", encoding="utf-8") as f:
        json.dump(users, f, indent=4, ensure_ascii=False)

    request.session["user"] = {"student_id": student_id, "name": name}

    return RedirectResponse("/", status_code=302)

@router.get("/login")
async def login_form(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@router.post("/login")
async def login(request: Request, student_id: str = Form(...), name: str = Form(...)):
    users = load_users()
    for user in users:
        if user["student_id"] == student_id and user["name"] == name:
            request.session["user"] = user
            return RedirectResponse("/", status_code=302)
    return templates.TemplateResponse("login.html", {
        "request": request,
        "error": "일치하는 사용자가 없습니다."
    })

@router.get("/logout")
def logout(request: Request):
    request.session.clear()
    return RedirectResponse("/")

@router.get("/withdraw")
async def withdraw(request: Request):
    user = request.session.get("user")
    if not user:
        return RedirectResponse("/", status_code=302)

    student_id = user["student_id"]
    name = user["name"]

    try:
        users = load_users()
        users = [u for u in users if not (u["student_id"] == student_id and u["name"] == name)]
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
