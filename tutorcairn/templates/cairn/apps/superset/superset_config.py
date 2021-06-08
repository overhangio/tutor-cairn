import logging

from cachelib.redis import RedisCache
from celery.schedules import crontab

# https://superset.apache.org/docs/installation/configuring-superset
SECRET_KEY = "{{ CAIRN_SUPERSET_SECRET_KEY }}"
SQLALCHEMY_DATABASE_URI = "postgresql+psycopg2://{{ CAIRN_POSTGRESQL_USER }}:{{ CAIRN_POSTGRESQL_PASSWORD }}@cairn-postgresql/{{ CAIRN_POSTGRESQL_DB }}"

DATA_CACHE_CONFIG = {
    "CACHE_TYPE": "redis",
    "CACHE_DEFAULT_TIMEOUT": 60 * 60 * 24,  # 1 day default (in secs)
    "CACHE_KEY_PREFIX": "superset_results",
    "CACHE_REDIS_URL": "redis://redis:6379/0",
}
CACHE_CONFIG = DATA_CACHE_CONFIG

# Borrowed from superset/docker/pythonpath_dev/superset_config.py
REDIS_HOST = "redis"
REDIS_PORT = "6379"
REDIS_CELERY_DB = 0
REDIS_RESULTS_DB = 1
RESULTS_BACKEND = RedisCache(host="redis", port=6379, key_prefix="superset_results")

class CeleryConfig:  # pylint: disable=too-few-public-methods
    BROKER_URL = f"redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_CELERY_DB}"
    CELERY_IMPORTS = ("superset.sql_lab", "superset.tasks")
    CELERY_RESULT_BACKEND = f"redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_RESULTS_DB}"
    CELERYD_LOG_LEVEL = "DEBUG"
    CELERYD_PREFETCH_MULTIPLIER = 1
    CELERY_ACKS_LATE = False
    CELERY_ANNOTATIONS = {
        "sql_lab.get_sql_results": {"rate_limit": "100/s"},
        "email_reports.send": {
            "rate_limit": "1/s",
            "time_limit": 120,
            "soft_time_limit": 150,
            "ignore_result": True,
        },
    }
    CELERYBEAT_SCHEDULE = {
        "email_reports.schedule_hourly": {
            "task": "email_reports.schedule_hourly",
            "schedule": crontab(minute=1, hour="*"),
        },
        "reports.scheduler": {
            "task": "reports.scheduler",
            "schedule": crontab(minute="*", hour="*"),
        },
        "reports.prune_log": {
            "task": "reports.prune_log",
            "schedule": crontab(minute=0, hour=0),
        },
    }


CELERY_CONFIG = CeleryConfig

# Avoid duplicate logging because of propagation to root logger
logging.getLogger("superset").propagate = False

# Enable some custom feature flags
# Do this once native filters are fully functional https://github.com/apache/superset/projects/15+
# def get_cairn_feature_flags(flags):
#     flags["DASHBOARD_NATIVE_FILTERS"] = True
#     return flags
# GET_FEATURE_FLAGS_FUNC = get_cairn_feature_flags
