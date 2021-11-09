FROM docker.io/yandex/clickhouse-server:21.11.3.6

RUN apt update && apt install -y python3
COPY ./scripts /scripts
RUN chmod a+x /scripts/*
ENV PATH /scripts:${PATH}
