## 실행 ##
>uvicorn main:app --reload --port=0

## 프로젝트 구조 ##
my_todo_app/
├── main.py
├── todo.json
├── requirements.txt
├── README.md
└── templates/
        └── index.html

`main.py`:  FastAPI 백엔드 서버를 설정하는 메인 파일

    def load_todos()
# todo.json이 존재하면 데이터를 불러오고, 존재하지 않으면 빈 리스트를 반환

    def save_todos(todos)
# To-Do 리스트 데이터를 JSON 파일에 저장하는 역할을 함

    def get_todos()
# todo.json에서 저장된 To-Do 데이터를 가져옴
# 터미널에 현재 불러온 To-Do 데이터를 출력하여 디버깅에 활용할 수 있도록 함

    def create_todo(todo: TodoItem)
# 새로운 To-Do 항목을 생성하여 todo.json에 저장하는 역할을 함

    def get_todo(todo_id: int)
# 클라이언트가 요청한 todo_id와 일치하는 항목을 찾으면 즉시 반환
# todo_id를 가진 항목이 리스트에 없으면 HTTP 404 오류 반환

    def update_todo(todo_id: int, updated_todo: TodoItem)
# 요청한 todo_id와 일치하는 항목을 찾으면 클라이언트가 보낸 updated_todo 값으로 수정
# todo_id를 가진 항목이 리스트에 없으면 HTTP 404 오류 반환

    def delete_todo(todo_id: int)
# todo_id를 제외한 새로운 리스트 생성후 변경된 To-Do 리스트를 다시 todo.json에 저장
# 터미널에 삭제된된 To-Do id를 출력

    def read_root()
# 웹 브라우저에서 서버의 주소에 접속했을 때 index.html 파일을 반환하는 역할
1️⃣ 웹 브라우저가 GET / 요청을 보냄
2️⃣ 서버는 "templates/index.html" 파일을 열어 내용을 읽음
3️⃣ HTML 데이터를 HTMLResponse로 변환하여 클라이언트에 반환
4️⃣ 웹 브라우저가 응답을 받아 HTML 페이지를 표시

`todo.json`:  초기 데이터 저장을 위한 JSON 파일로, 앱 시작 시 빈 배열(`[]`)로 초기화한다

`requirements.txt`:  필요한 외부 라이브러리와 해당 버전을 명시하여, 프로젝트의 의존성을 관리하고 쉽게 설치할 수 있도록 도와주는 파일

`templates/index.html`:  기본적인 프론트엔드 뷰를 제공하는 HTML 파일