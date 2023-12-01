FROM python:3.8

RUN pip install --upgrade pip
RUN pip install Flask gunicorn numpy
RUN pip install importlib_metadata

COPY src/ app/

WORKDIR /app

RUN python setup.py install

ENV PORT 8080

CMD exec gunicorn --bind :$PORT --workers 1 --threads 8 app:app
