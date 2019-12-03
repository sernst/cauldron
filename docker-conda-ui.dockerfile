FROM continuumio/anaconda3:latest

LABEL maintainer="swernst@gmail.com"

COPY cauldron /cauldron_local/cauldron
COPY README.rst /cauldron_local/
COPY requirements.txt /cauldron_local/
COPY setup.cfg /cauldron_local/
COPY setup.py /cauldron_local/
COPY docker-run-ui.sh /cauldron_local/

WORKDIR /cauldron_local

RUN conda install -y conda-build git \
 && /opt/conda/bin/pip install -r /cauldron_local/requirements.txt \
 && python3 setup.py develop \
 && chmod -R 775 /cauldron_local \
 && ln -s /opt/conda/bin/pip /opt/conda/bin/pip3

WORKDIR /notebooks

EXPOSE 8899

ENTRYPOINT ["/bin/bash", "/cauldron_local/docker-run-ui.sh"]
CMD ["--port=8899"]
