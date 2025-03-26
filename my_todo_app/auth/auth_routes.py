from fastapi import APIRouter, Request
from fastapi.responses import RedirectResponse
from todolists.todo_service import get_todo_file
from authlib.integrations.starlette_client import OAuth
from starlette.config import Config
import os, json

router = APIRouter()

config = Config(".env")

oauth = OAuth(config)
oauth.register(
    name='google',
    client_id=config("GOOGLE_CLIENT_ID"),
    client_secret=config("GOOGLE_CLIENT_SECRET"),
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_kwargs={'scope': 'openid email profile'}
)

@router.get("/login")
async def login(request: Request):
    redirect_uri = request.url_for("auth_callback")
    return await oauth.google.authorize_redirect(request, redirect_uri)


@router.get("/auth/callback")
async def auth_callback(request: Request):
    token = await oauth.google.authorize_access_token(request)
    # user_info = await oauth.google.get("userinfo", token=token)
    user_info = await oauth.google.get( "https://openidconnect.googleapis.com/v1/userinfo", token=token)
    user_info = user_info.json()

    request.session["user"] = {
        "email": user_info["email"]
    }

    # 사용자 전용 파일 생성
    filepath = get_todo_file(request)
    if not os.path.exists(filepath):
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump([], f, indent=4, ensure_ascii=False)

    return RedirectResponse("/", status_code=302)



@router.get("/protected")
async def protected(request: Request):
    user = request.session.get('user')
    if user:
        return {"message": "로그인 성공", "user": user}
    return RedirectResponse(url="/login")

@router.get("/logout")
def logout(request: Request):
    request.session.clear()
    return RedirectResponse(url="/")