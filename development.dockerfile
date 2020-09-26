ARG PYTHON

FROM python:$PYTHON

COPY requirements.txt /build-data/requirements.txt

RUN pip install -r /build-data/requirements.txt --upgrade
