FROM python:3.7

MAINTAINER swernst@gmail.com

COPY requirements.txt /build_data/requirements.txt

RUN pip install -r /build_data/requirements.txt \
 && pip install plotly matplotlib bokeh seaborn

WORKDIR /

EXPOSE 5010
