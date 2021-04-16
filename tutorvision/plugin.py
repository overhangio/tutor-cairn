from glob import glob
import os

from .__about__ import __version__
from .cli import vision_command

HERE = os.path.abspath(os.path.dirname(__file__))

templates = os.path.join(HERE, "templates")

config = {
    "add": {
        "CLICKHOUSE_PASSWORD": "{{ 20|random_string }}",
        "POSTGRESQL_PASSWORD": "{{ 20|random_string }}",
        "REDASH_COOKIE_SECRET": "{{ 20|random_string }}",
        "REDASH_PASSWORD": "{{ 20|random_string }}",
        "REDASH_SECRET_KEY": "{{ 20|random_string }}",
    },
    "defaults": {
        "CLICKHOUSE_DOCKER_IMAGE": "docker.io/yandex/clickhouse-server:21.2.7.11",
        "RUN_CLICKHOUSE": True,
        "CLICKHOUSE_HOST": "vision-clickhouse",
        "CLICKHOUSE_HTTP_PORT": 8123,
        "CLICKHOUSE_PORT": 9000,
        "CLICKHOUSE_DATABASE": "openedx",
        "CLICKHOUSE_USERNAME": "openedx",
        "POSTGRESQL_USER": "redash",
        "POSTGRESQL_DB": "redash",
        "REDASH_DOCKER_IMAGE": "docker.io/redash/redash:9.0.0-beta.b42121",
        "REDASH_HOST": "vision.{{ LMS_HOST }}",
        "REDASH_USERNAME": "admin",
        "REDASH_EMAIL": "{{ CONTACT_EMAIL }}",
    },
}

hooks = {"init": ["vision-clickhouse", "vision-redash"]}
command = vision_command


def patches():
    all_patches = {}
    for path in glob(os.path.join(HERE, "patches", "*")):
        with open(path) as patch_file:
            name = os.path.basename(path)
            content = patch_file.read()
            all_patches[name] = content
    return all_patches
