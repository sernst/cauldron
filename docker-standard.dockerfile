FROM ubuntu:18.04

MAINTAINER swernst@gmail.com

ENV PYTHON_RELEASE 3.6
ENV PYTHON_VERSION 3.6.5

RUN apt-get -y --no-install-recommends update && \
    apt-get -y --no-install-recommends install \
        openssl libssl-dev \
        git \
        gcc \
        build-essential \
        zlib1g-dev \
        wget && \
    mkdir /source && \
    cd /source && \
    wget --no-check-certificate https://www.python.org/ftp/python/${PYTHON_VERSION}/Python-${PYTHON_VERSION}.tgz && \
    tar xzf Python-${PYTHON_VERSION}.tgz && \
    cd Python-${PYTHON_VERSION} && \
    export CPPFLAGS="-I/usr/include/openssl" && \
    ./configure && \
    make install && \
    rm -rf /source

COPY cauldron /cauldron_local/cauldron
COPY README.rst /cauldron_local/
COPY requirements.txt /cauldron_local/
COPY setup.cfg /cauldron_local/
COPY setup.py /cauldron_local/
COPY docker-run.sh /cauldron_local/

WORKDIR /cauldron_local

RUN pip3 install -r /cauldron_local/requirements.txt && \
    python3 setup.py develop && \
    chmod -R 775 /cauldron_local

EXPOSE 5010

CMD ["/bin/bash", "/cauldron_local/docker-run.sh"]
