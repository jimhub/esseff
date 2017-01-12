FROM python:2-alpine

ADD . /essef-src

WORKDIR /essef-src

RUN apk add --no-cache --update \
    gcc \
    py-yaml \
    py-pip \
    && python setup.py install

ENTRYPOINT ["esseff"]
