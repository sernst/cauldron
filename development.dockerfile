FROM python:3.8

COPY requirements.txt /build-data/requirements.txt

RUN pip install -r /build-data/requirements.txt --upgrade
