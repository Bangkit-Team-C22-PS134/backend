From python:3.9

RUN pip install -r requirments.txt

COPY src/ app/
COPY resources/ app/

WORKDIR /app

ENV PORT 8080

CMD exec gunicorn --bind :$PORT --workers 1 --threads 8 app:app