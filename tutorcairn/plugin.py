from __future__ import annotations

import os
import shlex
import typing as t
from glob import glob

import click
import importlib_resources
from tutor import hooks
from tutor.__about__ import __version_suffix__

from .__about__ import __version__

# Handle version suffix in nightly mode, just like tutor core
if __version_suffix__:
    __version__ += "-" + __version_suffix__

HERE = os.path.abspath(os.path.dirname(__file__))

config: t.Dict[str, t.Dict[str, t.Any]] = {
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
        "POSTGRESQL_HOST": "cairn-postgresql",
        "POSTGRESQL_PORT": "5432",
        "POSTGRESQL_DATABASE": "superset",
        "POSTGRESQL_USERNAME": "superset",
        "SUPERSET_DOCKER_IMAGE": "{{ DOCKER_REGISTRY }}overhangio/cairn-superset:{{ CAIRN_VERSION }}",
        "SUPERSET_LANGUAGE_CODE": "{{ LANGUAGE_CODE[:2] }}",
        # SSO
        "ENABLE_SSO": True,
        "SSO_CLIENT_ID": "cairn",
        # Vector
        # https://hub.docker.com/r/timberio/vector/tags
        # https://github.com/vectordotdev/vector/releases
        "VECTOR_DOCKER_IMAGE": "docker.io/timberio/vector:0.25.1-alpine",
        # Auto sync user roles
        "AUTH_ROLES_SYNC_AT_LOGIN": False,
    },
    "unique": {
        "CLICKHOUSE_PASSWORD": "{{ 20|random_string }}",
        "POSTGRESQL_PASSWORD": "{{ 20|random_string }}",
        "SUPERSET_SECRET_KEY": "{{ 20|random_string }}",
        "SSO_CLIENT_SECRET": "{{ 20|random_string }}",
    },
}

# Add configuration entries
hooks.Filters.CONFIG_DEFAULTS.add_items(
    [(f"CAIRN_{key}", value) for key, value in config.get("defaults", {}).items()]
)
hooks.Filters.CONFIG_UNIQUE.add_items(
    [(f"CAIRN_{key}", value) for key, value in config.get("unique", {}).items()]
)
hooks.Filters.CONFIG_OVERRIDES.add_items(list(config.get("overrides", {}).items()))

# Init scripts
for service in ["cairn-clickhouse", "cairn-superset", "cairn-openedx"]:
    with open(
        os.path.join(HERE, "templates", "cairn", "tasks", service, "init"),
        encoding="utf-8",
    ) as fi:
        task = fi.read()
    hooks.Filters.CLI_DO_INIT_TASKS.add_item((service, task))

# Docker images
hooks.Filters.IMAGES_BUILD.add_items(
    [
        (
            "cairn-clickhouse",
            ("plugins", "cairn", "build", "cairn-clickhouse"),
            "{{ CAIRN_CLICKHOUSE_DOCKER_IMAGE }}",
            (),
        ),
        (
            "cairn-superset",
            ("plugins", "cairn", "build", "cairn-superset"),
            "{{ CAIRN_SUPERSET_DOCKER_IMAGE }}",
            (),
        ),
    ]
)
hooks.Filters.IMAGES_PULL.add_items(
    [
        (
            "cairn-clickhouse",
            "{{ CAIRN_CLICKHOUSE_DOCKER_IMAGE }}",
        ),
        (
            "cairn-superset",
            "{{ CAIRN_SUPERSET_DOCKER_IMAGE }}",
        ),
    ]
)
hooks.Filters.IMAGES_PUSH.add_items(
    [
        (
            "cairn-superset",
            "{{ CAIRN_SUPERSET_DOCKER_IMAGE }}",
        ),
        (
            "cairn-clickhouse",
            "{{ CAIRN_CLICKHOUSE_DOCKER_IMAGE }}",
        ),
    ]
)


@hooks.Filters.APP_PUBLIC_HOSTS.add()
def _print_superset_host(
    hosts: list[str], context_name: t.Literal["local", "dev"]
) -> list[str]:
    if context_name == "dev":
        hosts.append("{{ CAIRN_HOST }}:2247")
    else:
        hosts.append("{{ CAIRN_HOST }}")
    return hosts


@click.command(
    name="cairn-createuser", help="Create a Cairn user, both in Clickhouse and Superset"
)
@click.option(
    "--bootstrap-dashboards",
    is_flag=True,
    help="Load the default Cairn dashboards to the user's Superset account",
)
@click.option("--admin", is_flag=True)
@click.option(
    "-p",
    "--password",
    help="Specify password from the command line. If undefined, no password will be set. (Ignored with SSO)",
    hide_input=True,
)
@click.option(
    "-c",
    "--course-id",
    "course_ids",
    help="Limit access to a selection of courses (Ignored with SSO).",
    multiple=True,
    hide_input=True,
)
@click.argument("username")
@click.argument("email")
def create_user_command(
    bootstrap_dashboards: bool,
    admin: bool,
    password: str,
    course_ids: list[str],
    username: str,
    email: str,
) -> t.Iterable[tuple[str, str]]:
    admin_opt = " --admin" if admin else ""

    # TODO can we now simplify the clickhouse image?
    # - get rid of the cairn utility
    # - remove the auth.json file

    create_superset_user = "python ./superset/cairn/ctl.py createuser"
    if password:
        create_superset_user += f" --password={shlex.quote(password)}"
    for course_id in course_ids:
        create_superset_user += f" --course-id={course_id}"
    create_superset_user += f" {admin_opt} {username} {email}"
    yield ("cairn-superset", create_superset_user)

    # Bootstrap dashboards
    if bootstrap_dashboards:
        yield (
            "cairn-superset",
            f"python ./superset/cairn/ctl.py bootstrap-dashboards {username} /app/bootstrap/courseoverview.json",
        )


hooks.Filters.CLI_DO_COMMANDS.add_item(create_user_command)

####### Boilerplate code
# Add the "templates" folder as a template root
hooks.Filters.ENV_TEMPLATE_ROOTS.add_item(
    str(importlib_resources.files("tutorcairn") / "templates")
)
# Render the "build" and "apps" folders
hooks.Filters.ENV_TEMPLATE_TARGETS.add_items(
    [
        ("cairn/build", "plugins"),
        ("cairn/apps", "plugins"),
    ],
)
# Load patches from files
for path in glob(str(importlib_resources.files("tutorcairn") / "patches" / "*")):
    with open(path, encoding="utf-8") as patch_file:
        hooks.Filters.ENV_PATCHES.add_item((os.path.basename(path), patch_file.read()))
