# Superset image with additional database drivers
# https://hub.docker.com/r/apache/superset
# https://superset.apache.org/docs/databases/installing-database-drivers
FROM docker.io/apache/superset:1.3.2

USER root

# https://pypi.org/project/clickhouse-driver/
# https://pypi.org/project/clickhouse-sqlalchemy/
# https://pypi.org/project/mysqlclient/
RUN pip install clickhouse-driver==0.2.2 mysqlclient==2.1.0
RUN pip install clickhouse-sqlalchemy==0.1.7

COPY --chown=superset:superset ./scripts /scripts
RUN chmod a+x /scripts/*
ENV PATH /scripts:${PATH}

USER superset

HEALTHCHECK CMD curl -f "http://localhost:8000"

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
