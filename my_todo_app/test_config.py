import bcrypt

# 실제 로그인 테스트에서 사용할 사용자
PLAIN_PASSWORD = "mypassword"
HASHED_PASSWORD = bcrypt.hashpw(
    PLAIN_PASSWORD.encode("utf-8"), bcrypt.gensalt()
).decode("utf-8")

TEST_USER = {
    "student_id": "20231234",
    "name": "테스트학생",
    "id": "test_google_id",
    "password": HASHED_PASSWORD,
}

# 로그인 실패 테스트용 비밀번호
WRONG_PASSWORD = "wrongpassword"
