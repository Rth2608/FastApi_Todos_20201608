FROM python:3.11

WORKDIR /app
COPY . /app/my_todo_app
COPY ../requirements.txt /app/requirements.txt

ENV PYTHONPATH=/app

RUN pip install --no-cache-dir -r /app/requirements.txt

CMD ["uvicorn", "my_todo_app.main:app", "--host", "0.0.0.0", "--port", "9000", "--reload"]