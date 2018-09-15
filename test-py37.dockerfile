FROM python:3.7

COPY requirements.txt /library/requirements.txt

RUN pip install -r /library/requirements.txt

COPY MANIFEST.in /library/MANIFEST.in
COPY README.rst /library/README.rst
COPY setup.cfg /library/setup.cfg
COPY setup.py /library/setup.py
COPY cauldron /library/cauldron

WORKDIR /library/

RUN python setup.py develop

WORKDIR /root/

ENTRYPOINT ['/bin/bash']
CMD []
