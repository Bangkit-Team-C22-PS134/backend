From python:3.9

COPY src/ app/src/
COPY src/key.json app/src/
COPY resources/ app/resources/
COPY requirements.txt .
RUN --mount=type=cache,target=/root/.cache \
    pip install -r requirements.txt


WORKDIR /app/src

ENV PORT 8080

CMD exec gunicorn --bind :$PORT --workers 1 --threads 8 app:app