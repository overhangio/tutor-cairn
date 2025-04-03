# Superset image with additional database drivers
# https://hub.docker.com/r/apache/superset
# https://github.com/apache/superset/releases
# https://github.com/apache/superset/blob/master/Dockerfile
# https://superset.apache.org/docs/databases/installing-database-drivers
FROM docker.io/apache/superset:4.0.0

USER root

# https://github.com/apache/superset/blob/4.0.0/Dockerfile#L109-L110
# Extracted from https://superset.apache.org/docs/installation/alerts-reports/#custom-dockerfile
ARG GECKODRIVER_VERSION=v0.33.0 \
    FIREFOX_VERSION=117.0.1

RUN apt-get update -qq \
    && apt-get install -yqq --no-install-recommends \
        libnss3 \
        libdbus-glib-1-2 \
        libgtk-3-0 \
        libx11-xcb1 \
        libasound2 \
        libxtst6 \
        wget \
        pkg-config \
    # Install GeckoDriver WebDriver
    && wget -q https://github.com/mozilla/geckodriver/releases/download/${GECKODRIVER_VERSION}/geckodriver-${GECKODRIVER_VERSION}-linux64.tar.gz -O - | tar xfz - -C /usr/local/bin \
    # Install Firefox
    && wget -q https://download-installer.cdn.mozilla.net/pub/firefox/releases/${FIREFOX_VERSION}/linux-x86_64/en-US/firefox-${FIREFOX_VERSION}.tar.bz2 -O - | tar xfj - -C /opt \
    && ln -s /opt/firefox/firefox /usr/local/bin/firefox \
    && apt-get autoremove -yqq --purge wget && rm -rf /var/[log,tmp]/* /tmp/* /var/lib/apt/lists/*

# https://pypi.org/project/clickhouse-driver/
# https://pypi.org/project/mysqlclient/
# https://pypi.org/project/clickhouse-connect/
# https://pypi.org/project/clickhouse-sqlalchemy/
# https://pypi.org/project/Authlib/
# We preserve the clickhouse-sqlalchemy package to keep backward compatibility with existing dashboards
RUN --mount=type=cache,target=/root/.cache/pip,sharing=shared pip install \
    clickhouse-driver==0.2.7 \
    mysqlclient==2.2.4 \
    clickhouse-connect==0.7.8 \
    clickhouse-sqlalchemy==0.2.4 \
    authlib==1.3.0

USER superset

# Copy lib
COPY --chown=superset:superset ./cairn /app/superset/cairn

# This is required to have a proper healthcheck
ENV SUPERSET_PORT=2247

ENTRYPOINT []
CMD gunicorn \
    --bind  "0.0.0.0:2247" \
    --access-logfile '-' \
    --error-logfile '-' \
    --workers 2 \
    --worker-class gthread \
    --threads 20 \
    --timeout 60 \
    --limit-request-line 0 \
    --limit-request-field_size 0 \
    "${FLASK_APP}"
