from fastapi.testclient import TestClient
from my_todo_app.main import app

client = TestClient(app)

def test_get_login_page():
    response = client.get("/login")
    assert response.status_code == 200
    assert "로그인" in response.text or "Login" in response.text

def test_get_register_page():
    response = client.get("/register")
    assert response.status_code == 200
    assert "회원가입" in response.text or "Register" in response.text

def test_post_login_fail():
    data = {
        "student_id": "wronguser",
        "password": "wrongpass"
    }
    response = client.post("/login", data=data, follow_redirects=False)
    assert response.status_code == 200
    assert "등록되지 않은 학번" in response.text or "비밀번호가 틀렸습니다" in response.text



def test_post_register_redirect():
    # 세션 주입 먼저
    client.get("/test/set-temp-user")

    data = {
        "student_id": "99999999",
        "name": "테스트학생",
        "password": "1234"
    }
    response = client.post("/register/submit", data=data, follow_redirects=False)
    assert response.status_code in [302]


def test_register_submit_redirect():
    # 임시 세션 없이 접근 → 리디렉트 발생 예상
    data = {
        "student_id": "20231234",
        "name": "테스트학생",
        "password": "pass1234"
    }
    response = client.post("/register/submit", data=data, follow_redirects=False)
    assert response.status_code == 302

def test_logout_redirect():
    client.get("/test/set-login-user")
    response = client.get("/logout", follow_redirects=False)
    assert response.status_code in [302, 307]  # ✅ 여기 수정
    assert response.headers["location"] == "/"



def test_withdraw_success():
    client.get("/test/set-login-user")

    # login_data에 유저가 있어야 정상 탈퇴되므로 미리 넣기
    import os, json
    os.makedirs("login_data", exist_ok=True)
    with open("login_data/login.json", "w", encoding="utf-8") as f:
        json.dump([{
            "student_id": "20231234",
            "name": "테스트학생",
            "id": "test_google_id",
            "password": "fakehash"
        }], f, indent=4, ensure_ascii=False)

    response = client.get("/withdraw", follow_redirects=False)
    assert response.status_code == 302
    assert response.headers["location"] == "/"
