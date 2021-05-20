# Superset image with additional database drivers
# https://hub.docker.com/r/apache/superset
# https://superset.apache.org/docs/databases/installing-database-drivers
FROM docker.io/apache/superset:a9d888ad402ebb35da45df446997c426d6abee9d

USER root
# https://pypi.org/project/clickhouse-driver/
# https://pypi.org/project/clickhouse-sqlalchemy/
# https://pypi.org/project/mysqlclient/
RUN pip install clickhouse-driver==0.2.0 clickhouse-sqlalchemy==0.1.6 mysqlclient==2.0.3

COPY ./scripts /scripts
RUN chmod a+x /scripts/*
ENV PATH /scripts:${PATH}

USER superset

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
