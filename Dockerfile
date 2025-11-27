FROM python:3.12-slim

WORKDIR /usr/src/app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

COPY pyproject.toml poetry.lock* /usr/src/app/
RUN pip install --upgrade pip && pip install "poetry==1.8.3" && poetry config virtualenvs.create false && poetry install --no-root

COPY . /usr/src/app

CMD ["uvicorn", "app.asgi:app", "--host", "0.0.0.0", "--port", "8000"]
