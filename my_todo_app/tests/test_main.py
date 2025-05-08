import os
import json
import pytest
from fastapi.testclient import TestClient
from bs4 import BeautifulSoup
from my_todo_app.main import app
from my_todo_app.test_config import TEST_USER, WRONG_PASSWORD

client = TestClient(app)


@pytest.fixture(scope="session", autouse=True)
def set_test_env():
    os.environ["ENV"] = "test"


# ---------- 공통 유틸 ----------
def setup_user_session():
    client.get("/test/set-login-user")


# ---------- 루트 페이지 ----------
def test_read_root():
    response = client.get("/")
    assert response.status_code == 200
    assert "로그인" in response.text


def test_root_with_login():
    setup_user_session()
    response = client.get("/")
    assert response.status_code == 200
    assert "로그아웃" in response.text or "할 일 목록" in response.text


# ---------- 로그인 / 회원가입 ----------
def test_get_login_page():
    response = client.get("/login")
    assert response.status_code == 200
    assert "로그인" in response.text


def test_get_register_page():
    response = client.get("/register")
    assert response.status_code == 200
    assert "회원가입" in response.text


def test_post_login_fail():
    data = {"student_id": "wronguser", "password": WRONG_PASSWORD}
    response = client.post("/login", data=data)
    assert response.status_code == 200
    assert (
        "등록되지 않은 학번" in response.text
        or "비밀번호가 틀렸습니다" in response.text
    )


def test_post_login_success():
    os.makedirs("login_data", exist_ok=True)
    with open("login_data/login.json", "w", encoding="utf-8") as f:
        json.dump([TEST_USER], f, indent=4, ensure_ascii=False)

    data = {"student_id": TEST_USER["student_id"], "password": "mypassword"}
    response = client.post("/login", data=data, follow_redirects=True)
    assert response.status_code == 200
    assert "로그아웃" in response.text


def test_post_register_redirect():
    client.get("/test/set-temp-user")
    data = {"student_id": "99999999", "name": "테스트학생", "password": "mypassword"}
    response = client.post("/register/submit", data=data, follow_redirects=False)
    assert response.status_code == 302


def test_register_submit_redirect():
    data = {"student_id": "20231234", "name": "테스트학생", "password": "mypassword"}
    response = client.post("/register/submit", data=data, follow_redirects=False)
    assert response.status_code == 302


def test_register_existing_student_id():
    os.makedirs("login_data", exist_ok=True)
    with open("login_data/login.json", "w", encoding="utf-8") as f:
        json.dump([TEST_USER], f, indent=4, ensure_ascii=False)

    client.get("/test/set-temp-user")
    data = {
        "student_id": TEST_USER["student_id"],
        "name": TEST_USER["name"],
        "password": "mypassword",
    }
    response = client.post("/register/submit", data=data)
    assert response.status_code == 200

    soup = BeautifulSoup(response.text, "html.parser")
    text = soup.get_text()
    assert (
        "이미 존재하는 학번" in text
        or "다른 학번으로 시도해주세요" in text
        or "❌ 이미 존재하는 학번입니다." in text
    )


def test_register_submit_without_temp_user():
    data = {"student_id": "12345678", "name": "홍길동", "password": "ValidPass123!"}
    response = client.post("/register/submit", data=data, follow_redirects=False)
    assert response.status_code == 302
    assert response.headers["location"] == "/"


def test_logout_redirect():
    setup_user_session()
    response = client.get("/logout", follow_redirects=False)
    assert response.status_code in [302, 307]
    assert response.headers["location"] == "/"


def test_logout_without_login():
    response = client.get("/logout", follow_redirects=False)
    assert response.status_code in [302, 307]
    assert response.headers["location"] == "/"


def test_withdraw_success():
    setup_user_session()
    os.makedirs("login_data", exist_ok=True)
    with open("login_data/login.json", "w", encoding="utf-8") as f:
        json.dump([TEST_USER], f, indent=4, ensure_ascii=False)

    response = client.get("/withdraw", follow_redirects=False)
    assert response.status_code == 302
    assert response.headers["location"] == "/"


def test_withdraw_without_login():
    client.get("/logout")
    response = client.get("/withdraw", follow_redirects=False)
    assert response.status_code == 302
    assert response.headers["location"] == "/"


# ---------- 할 일 ----------
def test_get_todos():
    setup_user_session()
    response = client.get("/api/todos")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_save_todos():
    setup_user_session()
    new_todos = [
        {"id": 1, "task": "테스트 할 일 1"},
        {"id": 2, "task": "테스트 할 일 2"},
    ]
    response = client.post("/api/todos", json=new_todos)
    assert response.status_code == 200
    assert response.json().get("message") == "저장 완료"


# ---------- 추가 테스트 ----------
def test_check_student_id_exists():
    os.makedirs("login_data", exist_ok=True)
    with open("login_data/login.json", "w", encoding="utf-8") as f:
        json.dump([TEST_USER], f, indent=4, ensure_ascii=False)

    response = client.get(f"/check-student-id?student_id={TEST_USER['student_id']}")
    assert response.status_code == 200
    assert response.json()["exists"] is True


def test_check_student_id_not_exists():
    response = client.get("/check-student-id?student_id=notexist123")
    assert response.status_code == 200
    assert response.json()["exists"] is False


def test_get_register_page_without_temp_user():
    response = client.get("/register")
    assert response.status_code == 200
    assert "회원가입" in response.text


def test_auth_callback_direct_access_without_oauth(monkeypatch):
    monkeypatch.setenv("ENV", "test")
    response = client.get("/auth/callback", follow_redirects=False)
    assert response.status_code in [400, 422, 404]


def test_withdraw_file_delete_fail(monkeypatch):
    setup_user_session()
    os.makedirs("login_data", exist_ok=True)
    with open("login_data/login.json", "w", encoding="utf-8") as f:
        json.dump([TEST_USER], f, indent=4, ensure_ascii=False)

    monkeypatch.setattr(
        os, "remove", lambda path: (_ for _ in ()).throw(OSError("삭제 오류"))
    )
    response = client.get("/withdraw")
    assert response.status_code == 500
    assert "탈퇴 중 오류 발생" in response.text or response.json().get("error")


def test_set_temp_user():
    response = client.get("/test/set-temp-user")
    assert response.status_code == 200
    assert response.json()["ok"] is True
