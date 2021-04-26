import click

from tutor import config as tutor_config
from tutor.commands.compose import ComposeJobRunner
from tutor.commands.local import docker_compose as local_docker_compose


@click.group(help="Manage your Vision platform")
def vision_command():
    pass


@click.group(help="Manage datalake access")
def datalake():
    pass


@click.command(name="createuser", help="Create new user or update existing one")
@click.argument("username")
@click.pass_obj
def datalake_createuser(context, username):
    run_datalake_query(context.root, f"CREATE USER OR REPLACE {username}")


@click.command(name="setpermissions", help="Restrict user access")
@click.argument("username")
@click.option(
    "-c",
    "--course-id",
    "course_ids",
    multiple=True,
    help=(
        "Grant access to a course data. This option may be used multiple times to grant "
        "access to multiple courses."
    ),
)
@click.pass_obj
def datalake_setpermissions(context, username, course_ids):
    condition = "1"
    if course_ids:
        condition = " OR ".join(
            [
                "course_id = '{course_id}'".format(course_id=course_id)
                for course_id in course_ids
            ]
        )
    # TODO rename courseenrollments to course_enrollments (and other tables as well)
    # Note that the "CREATE TEMPORARY TABLE" grant is required to make use of "numbers()" functions.
    query = f"""
GRANT CREATE TEMPORARY TABLE ON *.* TO {username};

GRANT SELECT ON events TO {username};
CREATE ROW POLICY OR REPLACE {username} ON events AS RESTRICTIVE FOR SELECT USING {condition} TO {username};

GRANT SELECT ON coursegrades TO {username};
CREATE ROW POLICY OR REPLACE {username} ON coursegrades AS RESTRICTIVE FOR SELECT USING {condition} TO {username};

GRANT SELECT ON courseenrollments TO {username};
CREATE ROW POLICY OR REPLACE {username} ON courseenrollments AS RESTRICTIVE FOR SELECT USING {condition} TO {username};

GRANT SELECT ON video_events TO {username};
CREATE ROW POLICY OR REPLACE {username} ON video_events AS RESTRICTIVE FOR SELECT USING {condition} TO {username};

GRANT SELECT ON video_view_segments TO {username};
CREATE ROW POLICY OR REPLACE {username} ON video_view_segments AS RESTRICTIVE FOR SELECT USING {condition} TO {username};
"""
    run_datalake_query(context.root, query)


def run_datalake_query(root, query):
    config = tutor_config.load(root)
    command = f"""clickhouse client \
    --host={config["VISION_CLICKHOUSE_HOST"]} \
    --port={config["VISION_CLICKHOUSE_PORT"]} \
    --user={config["VISION_CLICKHOUSE_USERNAME"]} \
    --password={config["VISION_CLICKHOUSE_PASSWORD"]} \
    --database={config["VISION_CLICKHOUSE_DATABASE"]} \
    --multiline --multiquery \
    --query "{query}"
    """
    runner = ComposeJobRunner(root, config, local_docker_compose)
    runner.run_job("vision-clickhouse", command)


@click.group(name="frontend", help="Manage the frontend access")
def frontend_command():
    pass


@click.command(name="createuser", help="Create a new user to access the frontend")
@click.option(
    "-p",
    "--password",
    default="",
    prompt="User password",
    hide_input=True,
    confirmation_prompt=True,
    help="User password: if undefined you will be prompted to input a password",
)
@click.option(
    "-r",
    "--root",
    "is_root",
    is_flag=True,
    default=False,
    help="Grant root/administration privileges on the frontend to this user",
)
@click.argument("username")
@click.argument("email")
@click.pass_obj
def frontend_createuser(context, password, is_root, username, email):
    config = tutor_config.load(context.root)
    config.update(
        {
            "password": password,
            "is_root": is_root,
            "username": username,
            "email": email,
        }
    )
    runner = ComposeJobRunner(context.root, config, local_docker_compose)
    runner.run_job_from_template(
        "vision-redash", "vision", "hooks", "vision-redash", "createuser"
    )


datalake.add_command(datalake_createuser)
datalake.add_command(datalake_setpermissions)
vision_command.add_command(datalake)
frontend_command.add_command(frontend_createuser)
vision_command.add_command(frontend_command)
