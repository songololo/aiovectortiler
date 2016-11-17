# docker build --tag='shongololo/aiovectortiler' --file='aiovectortiler/example_configs/Dockerfile' .

FROM ubuntu:16.04
MAINTAINER Gareth Simons <garethsimons@me.com>

RUN apt-get update \
    && apt-get install -y git build-essential python3 python3-pip python3-shapely \
    && pip3 install pip --upgrade \
    && pip3 install PyYAML aiohttp aiohttp-cors asyncpg \
    mapbox-vector-tile mercantile 'protobuf>=3.0.0' ujson

COPY aiovectortiler /aiovectortiler

VOLUME /configs/

EXPOSE 8080

CMD ["python3", "/aiovectortiler/aiovectortiler/serve.py", "--server_configs=/configs/server_configs.yaml", "--layer_recipes=/configs/layer_recipes/"]