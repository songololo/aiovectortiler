# docker build --tag='shongololo/aiovectortiler' --file='~/configs/Dockerfile' .

FROM ubuntu:16.04
MAINTAINER Gareth Simons <garethsimons@me.com>

RUN apt-get update \
    && apt-get install -y git build-essential python3 python3-pip python3-shapely

RUN pip3 install pip --upgrade

RUN pip3 install PyYAML aiohttp aiohttp-cors asyncpg 'mapbox-vector-tile>=0.4.0' mercantile 'protobuf>=3.0.0' ujson

COPY . /aiovectortiler
RUN chmod -R 0755 /aiovectortiler

VOLUME /configs

EXPOSE 8080

CMD ["/usr/bin/python3", "/aiovectortiler/aiovectortiler/serve.py"]