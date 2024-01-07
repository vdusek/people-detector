# docker build --rm --tag people-detector ./

FROM python:3.7.16-bullseye

COPY requirements.txt .
COPY requirements-test.txt .

RUN pip install -r requirements.txt -r requirements-test.txt
