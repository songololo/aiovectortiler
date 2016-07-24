FROM ubuntu:16.04
MAINTAINER Gareth Simons <garethsimons@me.com>

RUN apt-get update \
    && apt-get install -y git build-essential python3 python3-pip python3-psycopg2 python3-shapely \
    && pip3 install pip --upgrade

RUN git clone https://github.com/shongololo/aiovectortiler.git
RUN pip3 install /aiovectortiler/.

EXPOSE 8080

CMD ["python3", "/aiovectortiler/aiovectortiler/serve.py"]