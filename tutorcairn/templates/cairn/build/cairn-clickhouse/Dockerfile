# https://hub.docker.com/r/clickhouse/clickhouse-server/tags
FROM docker.io/clickhouse/clickhouse-server:24.1.8.22

RUN apt update && apt install -y python3
COPY ./scripts /scripts
RUN chmod a+x /scripts/*
ENV PATH /scripts:${PATH}
