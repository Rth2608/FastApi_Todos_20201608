import os, json
from fastapi import APIRouter, Request, Form
from fastapi.responses import RedirectResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from authlib.integrations.starlette_client import OAuth
from starlette.config import Config

router = APIRouter()
templates = Jinja2Templates(directory="templates")

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
    os.makedirs("data", exist_ok=True)
    with open(LOGIN_FILE, "w", encoding="utf-8") as f:
        json.dump(users, f, indent=4, ensure_ascii=False)

@router.get("/register")
async def register(request: Request):
    redirect_uri = request.url_for("auth_callback")
    return await oauth.google.authorize_redirect(request, redirect_uri)

@router.get("/auth/callback")
async def auth_callback(request: Request):
    token = await oauth.google.authorize_access_token(request)
    user_info = await oauth.google.get("https://openidconnect.googleapis.com/v1/userinfo", token=token)
    user_info = user_info.json()
    request.session["temp_user"] = user_info
    return templates.TemplateResponse("register.html", {"request": request, "name": user_info["name"]})

@router.post("/register/submit")
async def register_submit(request: Request, student_id: str = Form(...)):
    user_info = request.session.pop("temp_user", None)
    if not user_info:
        return templates.TemplateResponse("register.html", {
            "request": request,
            "name": "알 수 없음",
            "error": "세션이 만료되었거나 잘못된 접근입니다. 다시 시도해주세요."
        })

    name = user_info.get("name")
    if not name:
        return templates.TemplateResponse("register.html", {
            "request": request,
            "name": "알 수 없음",
            "error": "사용자 이름 정보를 불러올 수 없습니다."
        })

    save_user(student_id, name)

    request.session["user"] = {
        "student_id": student_id,
        "name": name
    }

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

    login_file = "login_data/login.json"
    try:
        if os.path.exists(login_file):
            with open(login_file, "r", encoding="utf-8") as f:
                users = json.load(f)

            users = [u for u in users if not (u["student_id"] == student_id and u["name"] == name)]

            with open(login_file, "w", encoding="utf-8") as f:
                json.dump(users, f, indent=4, ensure_ascii=False)

        todo_path = f"todos/{student_id}_{name}.json"
        if os.path.exists(todo_path):
            os.remove(todo_path)

        request.session.clear()

        return RedirectResponse("/", status_code=302)

    except Exception as e:
        print(f"탈퇴 중 오류: {e}")
        return JSONResponse(status_code=500, content={"error": "탈퇴 중 오류 발생"})
