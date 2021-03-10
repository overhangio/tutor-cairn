from glob import glob
import os

from .__about__ import __version__

HERE = os.path.abspath(os.path.dirname(__file__))

templates = os.path.join(HERE, "templates")

config = {
    "add": {
        "REDASH_POSTGRESQL_PASSWORD": "{{ 20|random_string }}",
        "REDASH_COOKIE_SECRET": "{{ 20|random_string }}",
        "REDASH_ROOT_PASSWORD": "{{ 20|random_string }}",
        "REDASH_SECRET_KEY": "{{ 20|random_string }}",
    },
    "defaults": {
        "CLICKHOUSE_DOCKER_IMAGE": "docker.io/yandex/clickhouse-server:20.8.14.4",
        "RUN_CLICKHOUSE": True,
        "CLICKHOUSE_HOST": "vision-clickhouse",
        "CLICKHOUSE_HTTP_PORT": 8123,
        "CLICKHOUSE_PORT": 9000,
        "CLICKHOUSE_DATABASE": "openedx_{{ ID }}",
        "REDASH_DOCKER_IMAGE": "docker.io/redash/redash:8.0.0.b32245",
        "REDASH_POSTGRESQL_USER": "redash",
        "REDASH_POSTGRESQL_DB": "redash",
        "REDASH_HOST": "vision.{{ LMS_HOST }}",
        "REDASH_ROOT_USERNAME": "admin",
        "REDASH_ROOT_EMAIL": "{{ CONTACT_EMAIL }}",
    },
}

hooks = {"init": ["vision-clickhouse", "vision-redash"]}


def patches():
    all_patches = {}
    for path in glob(os.path.join(HERE, "patches", "*")):
        with open(path) as patch_file:
            name = os.path.basename(path)
            content = patch_file.read()
            all_patches[name] = content
    return all_patches
