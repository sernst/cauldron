FROM continuumio/anaconda3:latest

MAINTAINER swernst@gmail.com

COPY cauldron /cauldron_local/cauldron
COPY README.rst /cauldron_local/
COPY requirements.txt /cauldron_local/
COPY setup.cfg /cauldron_local/
COPY setup.py /cauldron_local/
COPY docker-run.sh /cauldron_local/

WORKDIR /cauldron_local

RUN conda install -y conda-build git && \
    /opt/conda/bin/pip install -r /cauldron_local/requirements.txt && \
    python3.6 setup.py develop && \
    chmod -R 775 /cauldron_local

EXPOSE 5010

CMD ["/bin/bash", "/cauldron_local/docker-run.sh"]
