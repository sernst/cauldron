FROM continuumio/anaconda3

RUN apt-get -y install vim && \
    conda install -y conda-build git && \
    mkdir /build_data

COPY requirements.txt /build_data/requirements.txt

RUN /opt/conda/bin/pip install -r /build_data/requirements.txt && \
    /opt/conda/bin/pip install plotly

WORKDIR /

EXPOSE 5010
