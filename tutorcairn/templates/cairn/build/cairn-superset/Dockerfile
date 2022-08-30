# Superset image with additional database drivers
# https://hub.docker.com/r/apache/superset
# https://github.com/apache/superset/releases
# https://github.com/apache/superset/blob/master/Dockerfile
# https://superset.apache.org/docs/databases/installing-database-drivers
FROM docker.io/apache/superset:2.0.0

USER root

# https://pypi.org/project/clickhouse-driver/
# https://pypi.org/project/mysqlclient/
# https://pypi.org/project/clickhouse-sqlalchemy/
RUN pip install clickhouse-driver==0.2.4 mysqlclient==2.1.1
# Later versions of clickhouse-sqlalchemy will not work.
# Note that this connector be replaced by clickhouse-connect in v2.0.1:
# https://github.com/apache/superset/pull/22039
RUN pip install clickhouse-sqlalchemy==0.1.10

COPY --chown=superset:superset ./scripts /scripts
RUN chmod a+x /scripts/*
ENV PATH /scripts:${PATH}

USER superset

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
