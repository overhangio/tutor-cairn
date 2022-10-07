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
        "DOCKER_HOST_SOCK_PATH": "/var/run/docker.sock",
        "HOST": "data.{{ LMS_HOST }}",
        # Clickhouse
        "RUN_CLICKHOUSE": True,
        "CLICKHOUSE_DOCKER_IMAGE": "{{ DOCKER_REGISTRY }}overhangio/cairn-clickhouse:{{ CAIRN_VERSION }}",
        "CLICKHOUSE_HOST": "cairn-clickhouse",
        "CLICKHOUSE_HTTP_PORT": 8123,
        "CLICKHOUSE_HTTP_SCHEME": "http",
        "CLICKHOUSE_PORT": 9000,
        "CLICKHOUSE_DATABASE": "openedx",
        "CLICKHOUSE_USERNAME": "openedx",
        # Superset/Postgresql
        "RUN_POSTGRESQL": True,
        "POSTGRESQL_DATABASE": "superset",
        "POSTGRESQL_USERNAME": "superset",
        "SUPERSET_DOCKER_IMAGE": "{{ DOCKER_REGISTRY }}overhangio/cairn-superset:{{ CAIRN_VERSION }}",
        "SUPERSET_LANGUAGE_CODE": "{{ LANGUAGE_CODE[:2] }}",
        # Vector
        "VECTOR_DOCKER_IMAGE": "docker.io/timberio/vector:0.24.1-alpine",
    },
}

hooks = {
    "build-image": {
        "cairn-clickhouse": "{{ CAIRN_CLICKHOUSE_DOCKER_IMAGE }}",
        "cairn-superset": "{{ CAIRN_SUPERSET_DOCKER_IMAGE }}",
    },
    "remote-image": {
        "cairn-clickhouse": "{{ CAIRN_CLICKHOUSE_DOCKER_IMAGE }}",
        "cairn-superset": "{{ CAIRN_SUPERSET_DOCKER_IMAGE }}",
    },
    "init": ["cairn-clickhouse", "cairn-superset", "cairn-openedx"],
}


def patches():
    all_patches = {}
    for path in glob(os.path.join(HERE, "patches", "*")):
        with open(path) as patch_file:
            name = os.path.basename(path)
            content = patch_file.read()
            all_patches[name] = content
    return all_patches
