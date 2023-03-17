# https://hub.docker.com/r/yandex/clickhouse-server/tags
FROM docker.io/yandex/clickhouse-server:22.1.3.7

# The clickhouse repo is currently unavailable in some parts of the world. If we don't
# remove this repo here then `apt update` will fail. Check if the problem is resolved with:
# curl https://repo.yandex.ru/clickhouse/deb/stable/
# The above command should be a 200, and not a 404.
RUN rm /etc/apt/sources.list.d/clickhouse.list
RUN apt update && apt install -y python3
COPY ./scripts /scripts
RUN chmod a+x /scripts/*
ENV PATH /scripts:${PATH}
