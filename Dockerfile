FROM python:3.7

RUN pip install Flask gunicorn


COPY src/ app/

WORKDIR /app

RUN python setup.py install

ENV PORT 8080

CMD exec gunicorn --bind :$PORT --workers 1 --threads 8 app:app
