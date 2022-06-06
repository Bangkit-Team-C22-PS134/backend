From python:3.9.11

COPY src/ app/src/
COPY resources/ app/resources/
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

WORKDIR /app
CMD exec python3 generate_saved_model

WORKDIR /app/src

ENV PORT 8080

CMD exec gunicorn --bind :$PORT --workers 1 --threads 8 app:app