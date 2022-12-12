from __future__ import annotations
from glob import glob
import os
import typing as t

import click
import pkg_resources

from tutor import hooks

from .__about__ import __version__

HERE = os.path.abspath(os.path.dirname(__file__))


hooks.Filters.CONFIG_UNIQUE.add_items(
    [
        ("CAIRN_CLICKHOUSE_PASSWORD", "{{ 20|random_string }}"),
        ("CAIRN_POSTGRESQL_PASSWORD", "{{ 20|random_string }}"),
        ("CAIRN_SUPERSET_SECRET_KEY", "{{ 20|random_string }}"),
    ]
)
hooks.Filters.CONFIG_DEFAULTS.add_items(
    [
        ("CAIRN_VERSION", __version__),
        ("CAIRN_DOCKER_HOST_SOCK_PATH", "/var/run/docker.sock"),
        ("CAIRN_HOST", "data.{{ LMS_HOST }}"),
        # Clickhouse
        ("CAIRN_RUN_CLICKHOUSE", True),
        (
            "CAIRN_CLICKHOUSE_DOCKER_IMAGE",
            "{{ DOCKER_REGISTRY }}overhangio/cairn-clickhouse:{{ CAIRN_VERSION }}",
        ),
        ("CAIRN_CLICKHOUSE_HOST", "cairn-clickhouse"),
        ("CAIRN_CLICKHOUSE_HTTP_PORT", 8123),
        ("CAIRN_CLICKHOUSE_HTTP_SCHEME", "http"),
        ("CAIRN_CLICKHOUSE_PORT", 9000),
        ("CAIRN_CLICKHOUSE_DATABASE", "openedx"),
        ("CAIRN_CLICKHOUSE_USERNAME", "openedx"),
        # Superset/Postgresql
        ("CAIRN_RUN_POSTGRESQL", True),
        ("CAIRN_POSTGRESQL_DATABASE", "superset"),
        ("CAIRN_POSTGRESQL_USERNAME", "superset"),
        (
            "CAIRN_SUPERSET_DOCKER_IMAGE",
            "{{ DOCKER_REGISTRY }}overhangio/cairn-superset:{{ CAIRN_VERSION }}",
        ),
        ("CAIRN_SUPERSET_LANGUAGE_CODE", "{{ LANGUAGE_CODE[:2] }}"),
        # Vector
        # https://hub.docker.com/r/timberio/vector/tags
        # https://github.com/vectordotdev/vector/releases
        ("CAIRN_VECTOR_DOCKER_IMAGE", "docker.io/timberio/vector:0.25.1-alpine"),
    ]
)

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
    help="Specify password from the command line. If undefined, you will be prompted to input a password",
    prompt=True,
    hide_input=True,
)
@click.argument("username")
@click.argument("email")
def create_user_command(
    bootstrap_dashboards: bool, admin: bool, password: str, username: str, email: str
) -> t.Iterable[tuple[str, str]]:
    admin_opt = " --admin" if admin else ""
    yield from [
        ("cairn-clickhouse", f"cairn createuser {username}"),
        (
            "cairn-superset",
            f"cairn createuser{admin_opt} --password={password} {username} {email}",
        ),
    ]
    if bootstrap_dashboards:
        yield (
            "cairn-superset",
            f"cairn bootstrap-dashboards {username} /app/bootstrap/courseoverview.json",
        )


hooks.Filters.CLI_DO_COMMANDS.add_item(create_user_command)

####### Boilerplate code
# Add the "templates" folder as a template root
hooks.Filters.ENV_TEMPLATE_ROOTS.add_item(
    pkg_resources.resource_filename("tutorcairn", "templates")
)
# Render the "build" and "apps" folders
hooks.Filters.ENV_TEMPLATE_TARGETS.add_items(
    [
        ("cairn/build", "plugins"),
        ("cairn/apps", "plugins"),
    ],
)
# Load patches from files
for path in glob(
    os.path.join(pkg_resources.resource_filename("tutorcairn", "patches"), "*")
):
    with open(path, encoding="utf-8") as patch_file:
        hooks.Filters.ENV_PATCHES.add_item((os.path.basename(path), patch_file.read()))
