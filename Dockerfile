FROM ubuntu:20.04
ENV PYTHONBUFFERED 1

RUN apt-get update && \
    apt-get install -y python3.8 python3-pip && \
    update-alternatives --install /usr/bin/python python /usr/bin/python3.8 1 && \
    update-alternatives --install /usr/bin/pip pip /usr/bin/pip3 1

RUN apt-get update && \
    apt-get install -y build-essential openssl libssl-dev libpq-dev

ADD server/requirements.txt /server/requirements.txt
RUN pip install -r /server/requirements.txt

ADD /server /server

WORKDIR /server

CMD honcho run prod
