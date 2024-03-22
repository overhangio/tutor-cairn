# https://hub.docker.com/r/yandex/clickhouse-server/tags
FROM docker.io/yandex/clickhouse-server:22.1.3.7

# The clickhouse repo is currently unavailable in some parts of the world. If we don't
# remove this repo here then `apt update` will fail. Check if the problem is resolved with:
# curl https://repo.yandex.ru/clickhouse/deb/stable/
# The above command should be a 200, and not a 404.
RUN rm /etc/apt/sources.list.d/clickhouse.list
RUN apt update && apt install -y git build-essential libssl-dev zlib1g-dev \
libbz2-dev libreadline-dev libsqlite3-dev wget curl llvm libncurses5-dev \
libncursesw5-dev xz-utils tk-dev libffi-dev liblzma-dev


COPY ./scripts /scripts
RUN chmod a+x /scripts/*
# Install pyenv
# https://www.python.org/downloads/
# https://github.com/pyenv/pyenv/releases
ARG PYTHON_VERSION=3.12.2
ENV PYENV_ROOT /opt/pyenv
RUN git clone https://github.com/pyenv/pyenv $PYENV_ROOT --branch v2.3.36 --depth 1
# Install Python
RUN $PYENV_ROOT/bin/pyenv install $PYTHON_VERSION


RUN $PYENV_ROOT/bin/pyenv global $PYTHON_VERSION


ENV PATH /opt/pyenv/shims:/opt/pyenv/bin:/scripts:${PATH}
