From python:3.9.11

COPY src/ app/src/
COPY resources/ app/resources/
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install pandas
RUN pip3 install pandas


WORKDIR /app/src

ENV PORT 8080

CMD exec gunicorn --bind :$PORT --workers 1 --threads 8 app:app