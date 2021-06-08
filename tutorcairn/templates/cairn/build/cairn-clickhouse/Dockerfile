FROM docker.io/yandex/clickhouse-server:21.2.7.11

RUN apt update && apt install -y python3
COPY ./scripts /scripts
RUN chmod a+x /scripts/*
ENV PATH /scripts:${PATH}
