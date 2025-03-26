import logging
import os
import typing as t

from cachelib.redis import RedisCache
from celery.schedules import crontab

from superset.extensions import security_manager
from superset.cairn import bootstrap as cairn_bootstrap
from superset.cairn import sso as cairn_sso

# https://superset.apache.org/docs/installation/configuring-superset
SECRET_KEY = "{{ CAIRN_SUPERSET_SECRET_KEY }}"
SQLALCHEMY_DATABASE_URI = "postgresql+psycopg2://{{ CAIRN_POSTGRESQL_USERNAME }}:{{ CAIRN_POSTGRESQL_PASSWORD }}@{{ CAIRN_POSTGRESQL_HOST }}:{{ CAIRN_POSTGRESQL_PORT }}/{{ CAIRN_POSTGRESQL_DATABASE }}"

# Caddy is running behind a proxy: Superset needs to handle x-forwarded-* headers
# https://flask.palletsprojects.com/en/latest/deploying/proxy_fix/
# https://superset.apache.org/docs/installation/configuring-superset/#configuration-behind-a-load-balancer
ENABLE_PROXY_FIX = True

# Superset 3.0 ships with a default CSP (Content Security Policy) configuration via Talisman(Forces all connects to https)
# https://preset.io/blog/superset-3-0-release-notes/#default-csp-is-now-in-place

{% if not ENABLE_HTTPS %}
TALISMAN_ENABLED = False
{% endif %}

# Languages
# https://github.com/apache/superset/blob/dc575080d7e43d40b1734bb8f44fdc291cb95b11/superset/config.py#L324
available_languages = {
    "de": {"flag": "de", "name": "German"},
    "en": {"flag": "us", "name": "English"},
    "es": {"flag": "es", "name": "Spanish"},
    "fr": {"flag": "fr", "name": "French"},
    "it": {"flag": "it", "name": "Italian"},
    "ja": {"flag": "jp", "name": "Japanese"},
    "ko": {"flag": "kr", "name": "Korean"},
    "nl": {"flag": "nl", "name": "Dutch"},
    "pt": {"flag": "pt", "name": "Portuguese"},
    "pt_BR": {"flag": "br", "name": "Brazilian Portuguese"},
    "ru": {"flag": "ru", "name": "Russian"},
    "sk": {"flag": "sk", "name": "Slovak"},
    "sl": {"flag": "si", "name": "Slovenian"},
    "uk": {"flag": "uk", "name": "Ukranian"},
    "zh": {"flag": "cn", "name": "Chinese"},    
}
{#- https://github.com/apache/superset/blob/master/docs/docs/contributing/translations.mdx#enabling-language-selection #}
enabled_language_codes = ["en"]
LANGUAGES = {}
if "{{ CAIRN_SUPERSET_LANGUAGE_CODE }}" in available_languages:
    enabled_language_codes.append("{{ CAIRN_SUPERSET_LANGUAGE_CODE }}")
    # Set the platform default language/locale
    BABEL_DEFAULT_LOCALE = "{{ CAIRN_SUPERSET_LANGUAGE_CODE }}"
for code in enabled_language_codes:
    LANGUAGES[code] = available_languages[code]

# Borrowed from superset/docker/pythonpath_dev/superset_config.py
REDIS_HOST = "{{ REDIS_HOST }}"
REDIS_PORT = "{{ REDIS_PORT }}"
# Be careful not to conflict with Open edX here
REDIS_CELERY_DB = {{ OPENEDX_CELERY_REDIS_DB + 2 }}
REDIS_CACHE_DB = {{ OPENEDX_CACHE_REDIS_DB + 2 }}

# Cache configuration
CACHE_CONFIG = {
    "CACHE_TYPE": "redis",
    "CACHE_DEFAULT_TIMEOUT": 60 * 60 * 24 * 1,  # 1 day default (in secs)
    "CACHE_KEY_PREFIX": "superset_data_cache",
    "CACHE_REDIS_URL": f"redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_CACHE_DB}",
}
DATA_CACHE_CONFIG = CACHE_CONFIG.copy()
FILTER_STATE_CACHE_CONFIG = CACHE_CONFIG.copy()
FILTER_STATE_CACHE_CONFIG.update({
    "CACHE_DEFAULT_TIMEOUT": 60 * 60 * 24 * 90,  # 90 days
    "REFRESH_TIMEOUT_ON_RETRIEVAL": True,
})
EXPLORE_FORM_DATA_CACHE_CONFIG  = CACHE_CONFIG.copy()
EXPLORE_FORM_DATA_CACHE_CONFIG.update({
    "CACHE_DEFAULT_TIMEOUT": 60 * 60 * 24 * 7,  # 7 days
    "REFRESH_TIMEOUT_ON_RETRIEVAL": True,
})
RESULTS_BACKEND = RedisCache(
    host=REDIS_HOST,
    port=REDIS_PORT,
    db=REDIS_CACHE_DB,
    key_prefix="superset_results",
)
OPENEDX_LMS_ROOT_URL = "{% if ENABLE_HTTPS %}https{% else %}http{% endif %}://{{ LMS_HOST }}"
OPENEDX_CMS_ROOT_URL = "{% if ENABLE_HTTPS %}https{% else %}http{% endif %}://{{ CMS_HOST }}"

if os.environ.get("FLASK_ENV") == "development":
    OPENEDX_LMS_ROOT_URL = "http://{{ LMS_HOST }}:8000"
    OPENEDX_CMS_ROOT_URL = "http://{{ CMS_HOST }}:8001"

{% if CAIRN_ENABLE_SSO %}
# Authentication
# https://superset.apache.org/docs/installation/configuring-superset/#custom-oauth2-configuration
# https://flask-appbuilder.readthedocs.io/en/latest/security.html#authentication-oauth
from flask_appbuilder.security.manager import AUTH_OAUTH
AUTH_TYPE = AUTH_OAUTH

OPENEDX_SSO_CLIENT_ID = "{{ CAIRN_SSO_CLIENT_ID }}"
if os.environ.get("FLASK_ENV") == "development":
    OPENEDX_SSO_CLIENT_ID = "{{ CAIRN_SSO_CLIENT_ID }}-dev"
OAUTH_PROVIDERS = [
    {
        "name": cairn_sso.OPENEDX_SSO_PROVIDER,
        "token_key": "access_token",
        "icon": "fa-right-to-bracket",
        "remote_app": {
            "client_id": OPENEDX_SSO_CLIENT_ID,
            "client_secret": "{{ CAIRN_SSO_CLIENT_SECRET }}",
            "client_kwargs": {"scope": "read"},
            "access_token_method": "POST",
            "api_base_url": f"{OPENEDX_LMS_ROOT_URL}",
            "access_token_url": f"{OPENEDX_LMS_ROOT_URL}/oauth2/access_token/",
            "authorize_url": f"{OPENEDX_LMS_ROOT_URL}/oauth2/authorize/",
        }
    }
]
CUSTOM_SECURITY_MANAGER = cairn_sso.OpenEdxSsoSecurityManager
# Update roles on login: this will cause all roles (except those that are preserved) to
# be ovewritten.
AUTH_ROLES_SYNC_AT_LOGIN = {{ CAIRN_AUTH_ROLES_SYNC_AT_LOGIN }}
# Login will create user
AUTH_USER_REGISTRATION = True
{% endif %}

class CeleryConfig:  # pylint: disable=too-few-public-methods
    BROKER_URL = f"redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_CELERY_DB}"
    CELERY_IMPORTS = ("superset.sql_lab", "superset.tasks","superset.tasks.thumbnails",)
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

# Email configuration
SMTP_HOST = "{{ SMTP_HOST }}"
SMTP_PORT = {{ SMTP_PORT }}
SMTP_STARTTLS = {{ SMTP_USE_TLS }}
SMTP_SSL = {{ SMTP_USE_SSL }}
SMTP_USER = "{{ SMTP_USERNAME }}" # use the empty string "" if using an unauthenticated SMTP server
SMTP_PASSWORD = "{{ SMTP_PASSWORD }}" # use the empty string "" if using an unauthenticated SMTP server
SMTP_MAIL_FROM = "{{ CONTACT_EMAIL }}"
EMAIL_REPORTS_SUBJECT_PREFIX = "[{{ PLATFORM_NAME }}] "

ALERT_REPORTS_NOTIFICATION_DRY_RUN = False
WEBDRIVER_BASEURL = "http://cairn-superset:2247/"
# The base URL for the email report hyperlinks.
WEBDRIVER_BASEURL_USER_FRIENDLY = "{{ CAIRN_HOST }}"

# Avoid duplicate logging because of propagation to root logger
logging.getLogger("superset").propagate = False

# https://github.com/apache/superset/blob/master/RESOURCES/FEATURE_FLAGS.md
FEATURE_FLAGS = {
    # Enable dashboard embedding
    "EMBEDDED_SUPERSET": True,
    # This feature is stable but known to have bugs from time to time
    # Alerts and Reports also do not work on arm64 base images
    "ALERT_REPORTS": True,
    
}

ENABLE_CORS=True
CORS_OPTIONS={
    "origins": [
    f"{OPENEDX_LMS_ROOT_URL}", 
    f"{OPENEDX_CMS_ROOT_URL}"
    ],
}

{{ patch("cairn-superset-settings") }}
