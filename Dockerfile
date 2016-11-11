FROM continuumio/anaconda3

RUN apt-get -y install vim && \
    mkdir /cauldron && \
    mkdir /commands

WORKDIR /commands

COPY ./requirements.txt /commands/
COPY ./docker/bin /commands/bin/
COPY ./docker/.bashrc /root/.bashrc

RUN chmod -R 775 /commands/bin && \
    /opt/conda/bin/pip install -r requirements.txt

WORKDIR /cauldron
