FROM python:3.7

ENV PYTHONUNBUFFERED=1
WORKDIR /code

COPY requirements.txt /code/
COPY phenotype-reactor.ini /code/
COPY manage.py /code/
COPY api /code/api

RUN pip install -r requirements.txt
