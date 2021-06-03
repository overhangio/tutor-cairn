from glob import glob
import os

from .__about__ import __version__

HERE = os.path.abspath(os.path.dirname(__file__))

templates = os.path.join(HERE, "templates")

config = {
    "add": {
        "CLICKHOUSE_PASSWORD": "{{ 20|random_string }}",
        "POSTGRESQL_PASSWORD": "{{ 20|random_string }}",
        "SUPERSET_SECRET_KEY": "{{ 20|random_string }}",
    },
    "defaults": {
        "VERSION": __version__,
        "CLICKHOUSE_DOCKER_IMAGE": "{{ DOCKER_REGISTRY }}overhangio/clickhouse:{{ VISION_VERSION }}",
        "RUN_CLICKHOUSE": True,
        "CLICKHOUSE_SCHEME": "http",
        "CLICKHOUSE_HOST": "vision-clickhouse",
        "CLICKHOUSE_HTTP_PORT": 8123,
        "CLICKHOUSE_PORT": 9000,
        "CLICKHOUSE_DATABASE": "openedx",
        "CLICKHOUSE_USERNAME": "openedx",
        "DOCKER_HOST": "/var/run/docker.sock",
        "POSTGRESQL_USER": "superset",
        "POSTGRESQL_DB": "superset",
        "RUN_CLICKHOUSE": True,
        "RUN_POSTGRESQL": True,
        "SUPERSET_DOCKER_IMAGE": "{{ DOCKER_REGISTRY }}overhangio/superset:{{ VISION_VERSION }}",
        "SUPERSET_HOST": "vision.{{ LMS_HOST }}",
        "SUPERSET_DATABASE": "openedx",
    },
}

hooks = {
    "build-image": {
        "vision-clickhouse": "{{ VISION_CLICKHOUSE_DOCKER_IMAGE }}",
        "vision-superset": "{{ VISION_SUPERSET_DOCKER_IMAGE }}"
    },
    "init": ["vision-clickhouse", "vision-superset", "vision-openedx"],
}


def patches():
    all_patches = {}
    for path in glob(os.path.join(HERE, "patches", "*")):
        with open(path) as patch_file:
            name = os.path.basename(path)
            content = patch_file.read()
            all_patches[name] = content
    return all_patches
