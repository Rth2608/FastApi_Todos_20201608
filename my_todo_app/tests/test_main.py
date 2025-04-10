from fastapi.testclient import TestClient
from my_todo_app.main import app  # ← 경로 정확하게 지정

client = TestClient(app)

def test_read_root():
    response = client.get("/")
    assert response.status_code == 200
    assert "Google계정 연동으로 회원가입" in response.text

