FROM ubuntu:18.04

MAINTAINER swernst@gmail.com

ARG PYTHON_RELEASE
ARG PYTHON_VERSION

RUN apt-get -y --no-install-recommends update \
 && apt-get -y --no-install-recommends install \
      build-essential \
      bzip2 \
      gcc \
      git \
      libbz2-dev \
      libffi-dev \
      libgdbm-dev \
      libgdbm-compat-dev \
      liblzma-dev \
      libncursesw5-dev \
      libreadline-dev \
      libsqlite3-dev \
      libssl-dev \
      openssl \
      sqlite3 \
      uuid-dev \
      wget \
      zlib1g-dev \
 && mkdir /source \
 && cd /source \
 && wget --no-check-certificate https://www.python.org/ftp/python/${PYTHON_VERSION}/Python-${PYTHON_VERSION}.tgz \
 && tar xzf Python-${PYTHON_VERSION}.tgz \
 && cd Python-${PYTHON_VERSION} \
 && export CPPFLAGS="-I/usr/include/openssl" \
 && ./configure \
 && make install \
 && rm -rf /source \
 && ln -s /usr/local/bin/pip3 /usr/local/bin/pip \
 && ln -s /usr/local/bin/python3 /usr/local/bin/python

COPY cauldron /cauldron_local/cauldron
COPY README.rst /cauldron_local/
COPY requirements.txt /cauldron_local/
COPY setup.cfg /cauldron_local/
COPY setup.py /cauldron_local/
COPY docker-run.sh /cauldron_local/

WORKDIR /cauldron_local

RUN pip3 install -r /cauldron_local/requirements.txt \
 && python3 setup.py develop \
 && chmod -R 775 /cauldron_local

EXPOSE 5010

CMD ["/bin/bash", "/cauldron_local/docker-run.sh"]
