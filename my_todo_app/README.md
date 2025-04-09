cd my_todo_app
uvicorn main:app --reload --port 9000

docker-compose down
docker-compose up --build
