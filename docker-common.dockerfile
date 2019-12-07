ARG PARENT

FROM $PARENT

LABEL maintainer="swernst@gmail.com"

WORKDIR /cauldron_local

COPY requirements.txt /cauldron_local/

RUN apt-get -y --no-install-recommends update \
 && apt-get -y --no-install-recommends install \
      nginx \
 && apt-get clean \
 && pip install gunicorn \
 && pip install -r /cauldron_local/requirements.txt

COPY cauldron /cauldron_local/cauldron
COPY README.rst /cauldron_local/
COPY setup.cfg /cauldron_local/
COPY setup.py /cauldron_local/

RUN python setup.py develop \
 && chmod -R 775 /cauldron_local

ARG TYPE

ENV PYTHONUNBUFFERED=1
ENV CAULDRON_CONTAINER_TYPE=$TYPE

COPY docker /launch

WORKDIR /notebooks

ENTRYPOINT ["/bin/bash", "/launch/run.sh"]
CMD []
