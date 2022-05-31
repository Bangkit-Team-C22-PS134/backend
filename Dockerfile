From python:3.9

COPY src/ app/src/
COPY resources/ app/resources/

RUN pip install Flask
RUN pip install itsdangerous
RUN pip install Jinja2
RUN pip install MarkupSafe
RUN pip install Werkzeug
RUN pip install click
RUN pip install colorama
RUN pip install flask_restful
RUN pip install gunicorn
RUN pip install firebase_admin
#RUN pip install tensorflow


WORKDIR /app/src

ENV PORT 8080

CMD exec gunicorn --bind :$PORT --workers 1 --threads 8 app:app