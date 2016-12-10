# docker build --tag='shongololo/aiovectortiler' --file='configs/docker_aiovectortiler/Dockerfile' .

# optionally use with docker run -d -p 80:80 -v /var/run/docker.sock:/tmp/docker.sock:ro jwilder/nginx-proxy
# in which case, launch multiple aiovectortiler containers at the same virtual host to load balance

FROM ubuntu:16.04
MAINTAINER Gareth Simons <garethsimons@me.com>

RUN apt-get update \
    && apt-get install -y git build-essential python3 python3-pip python3-shapely \
    && pip3 install pip --upgrade \
    && pip3 install PyYAML aiohttp aiohttp-cors asyncpg mercantile protobuf ujson uvloop
    && apt-get purge -y --auto-remove pip3 \
    && rm -rf /var/lib/apt/lists/*

RUN git clone https://github.com/tilezen/mapbox-vector-tile
WORKDIR /mapbox-vector-tile
RUN git checkout tags/v1.0.0
RUN /usr/bin/python3 setup.py install

WORKDIR /
ADD . /aiovectortiler
RUN chmod -R 0755 /aiovectortiler

VOLUME /configs

CMD ["/usr/bin/python3", "/aiovectortiler/aiovectortiler/serve.py"]