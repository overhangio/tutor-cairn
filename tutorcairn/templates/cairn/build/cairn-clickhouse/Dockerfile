# https://hub.docker.com/r/yandex/clickhouse-server/tags
FROM docker.io/yandex/clickhouse-server:21.11.6.7

RUN apt update && apt install -y python3
COPY ./scripts /scripts
RUN chmod a+x /scripts/*
ENV PATH /scripts:${PATH}
