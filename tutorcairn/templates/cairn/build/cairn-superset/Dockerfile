# Superset image with additional database drivers
# https://hub.docker.com/r/apache/superset
# https://github.com/apache/superset/releases
# https://github.com/apache/superset/blob/master/Dockerfile
# https://superset.apache.org/docs/databases/installing-database-drivers
FROM docker.io/apache/superset:4.0.0

USER root

# https://pypi.org/project/clickhouse-driver/
# https://pypi.org/project/mysqlclient/
# https://pypi.org/project/clickhouse-connect/
# https://pypi.org/project/clickhouse-sqlalchemy/
# https://pypi.org/project/Authlib/
# We preserve the clickhouse-sqlalchemy package to keep backward compatibility with existing dashboards
RUN apt-get update \
    && apt-get install -y \
        pkg-config

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
ENV SUPERSET_PORT=8000

ENTRYPOINT []
CMD gunicorn \
    --bind  "0.0.0.0:8000" \
    --access-logfile '-' \
    --error-logfile '-' \
    --workers 2 \
    --worker-class gthread \
    --threads 20 \
    --timeout 60 \
    --limit-request-line 0 \
    --limit-request-field_size 0 \
    "${FLASK_APP}"
