import os
import json
import uuid
import sys
from fastapi import FastAPI
from fastapi.testclient import TestClient
from starlette.middleware.sessions import SessionMiddleware

# sys.path에 프로젝트 루트 추가
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from my_todo_app.auth.auth_routes import router as auth_router
from my_todo_app.todolists.todo_routes import router as todo_router

app = FastAPI()
app.add_middleware(SessionMiddleware, secret_key="test-secret")
app.include_router(auth_router)
app.include_router(todo_router, prefix="/api")

client = TestClient(app)

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
LOGIN_FILE = os.path.join(BASE_DIR, "login_data", "login.json")


def clear_login_file():
    os.makedirs(os.path.dirname(LOGIN_FILE), exist_ok=True)
    if os.path.exists(LOGIN_FILE):
        os.remove(LOGIN_FILE)
    with open(LOGIN_FILE, "w", encoding="utf-8") as f:
        json.dump([], f)


def generate_user():
    sid = f"test_{uuid.uuid4().hex[:6]}"
    return {"student_id": sid, "name": "홍길동", "password": "pw1234"}


def test_auth_and_todo_flow():
    clear_login_file()
    TEST_USER = generate_user()
    TODO_FILE = os.path.join(
        BASE_DIR, f"todos/{TEST_USER['student_id']}_{TEST_USER['name']}.json"
    )
    if os.path.exists(TODO_FILE):
        os.remove(TODO_FILE)

    # 1. 학번 중복 없음
    res = client.get(f"/check-student-id?student_id={TEST_USER['student_id']}")
    assert res.status_code == 200
    assert res.json() == {"exists": False}

    # 2. 회원가입
    res = client.post("/register/submit", data=TEST_USER, follow_redirects=False)
    assert res.status_code == 302

    # 3. 중복 학번 확인
    res = client.get(f"/check-student-id?student_id={TEST_USER['student_id']}")
    assert res.status_code == 200
    assert res.json() == {"exists": True}

    # 4. 잘못된 비밀번호 로그인
    res = client.post(
        "/login",
        data={"student_id": TEST_USER["student_id"], "password": "wrongpw"},
        follow_redirects=False,
    )
    assert res.status_code == 200
    assert "비밀번호가 틀렸습니다" in res.text

    # 5. 존재하지 않는 학번 로그인
    res = client.post(
        "/login",
        data={"student_id": "nonexistent", "password": "1234"},
        follow_redirects=False,
    )
    assert res.status_code == 200
    assert "등록되지 않은 학번입니다" in res.text

    # 6. 로그인 성공
    res = client.post(
        "/login",
        data={"student_id": TEST_USER["student_id"], "password": TEST_USER["password"]},
        follow_redirects=False,
    )
    assert res.status_code == 302
    cookies = res.cookies

    # 7. ToDo 빈 조회
    res = client.get("/api/todos", cookies=cookies)
    assert res.status_code == 200
    assert res.json() == []

    # 8. ToDo 저장
    todo_data = [{"title": "과제", "task": "수학", "timestamp": "2025-01-01T00:00:00"}]
    res = client.post("/api/todos", json=todo_data, cookies=cookies)
    assert res.status_code == 200
    assert res.json()["message"] == "저장 완료"

    # 9. 저장된 ToDo 조회
    res = client.get("/api/todos", cookies=cookies)
    assert res.status_code == 200
    assert res.json() == todo_data

    # 10. 로그아웃
    res = client.get("/logout", cookies=cookies, follow_redirects=False)
    assert res.status_code in (302, 307)

    # 11. 로그아웃 후 접근 차단
    res = client.get("/api/todos")
    assert res.status_code == 401

    # 12. 인증 없이 탈퇴 → redirect
    res = client.get("/withdraw", follow_redirects=False)
    assert res.status_code == 302

    # 13. 재로그인 후 탈퇴
    res = client.post(
        "/login",
        data={"student_id": TEST_USER["student_id"], "password": TEST_USER["password"]},
        follow_redirects=False,
    )
    cookies = res.cookies
    res = client.get("/withdraw", cookies=cookies, follow_redirects=False)
    assert res.status_code == 302
