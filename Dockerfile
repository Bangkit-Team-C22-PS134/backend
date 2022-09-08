From python:3.9.11

COPY src/ src/
COPY resources/ resources/
COPY requirements.txt .

RUN pip install --upgrade cython
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install pandas
RUN pip3 install pandas


WORKDIR /src

ENV PORT 8080

CMD exec gunicorn --bind :$PORT --workers 1 --threads 8 app:app