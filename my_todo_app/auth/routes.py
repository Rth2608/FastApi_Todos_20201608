from fastapi import APIRouter, Request
from fastapi.responses import RedirectResponse
from auth.config import oauth

router = APIRouter()

@router.get("/login")
async def login(request: Request):
    redirect_uri = request.url_for('auth')
    return await oauth.google.authorize_redirect(request, redirect_uri)

@router.get("/auth")
async def auth(request: Request):
    token = await oauth.google.authorize_access_token(request)
    resp = await oauth.google.get('userinfo', token=token)
    user = resp.json()
    request.session['user'] = dict(user)
    return RedirectResponse(url="/protected")

@router.get("/protected")
async def protected(request: Request):
    user = request.session.get('user')
    if user:
        return {"message": "로그인 성공", "user": user}
    return RedirectResponse(url="/login")