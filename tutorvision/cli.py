# TODO delete this module
# import click
#
# from tutor import config as tutor_config
# from tutor.commands.compose import ComposeJobRunner
# from tutor.commands.local import docker_compose as local_docker_compose
#
#
# @click.group(help="Manage your Vision platform")
# def vision_command():
#     pass
#
#
# @click.group(help="Print convenient commands that can be sent to the right containers", name="print")
# def print_command():
#     pass
#
#
# @click.command(name="datalake-create-user", help="Print user creation query")
# @click.argument("username")
# @click.pass_obj
# def print_datalakecreateuser(context, username):
#     print(f"CREATE USER IF NOT EXISTS {username}")
#
#
# # @click.command(name="setpermissions", help="Restrict user access")
# # @click.argument("username")
# # @click.option(
# #     "-c",
# #     "--course-id",
# #     "course_ids",
# #     multiple=True,
# #     help=(
# #         "Grant access to a course data. This option may be used multiple times to grant "
# #         "access to multiple courses."
# #     ),
# # )
# # @click.option(
# #     "-o",
# #     "--org-id",
# #     "org_ids",
# #     multiple=True,
# #     help=(
# #         "Grant access to the course data of an organization. This option may be used multiple times to grant "
# #         "access to multiple organizations."
# #     ),
# # )
# # @click.pass_obj
# # def datalake_setpermissions(context, username, course_ids, org_ids):
# #     conditions = []
# #     for course_id in course_ids:
# #         conditions.append(f"course_id = '{course_id}'")
# #     for org_id in org_ids:
# #         conditions.append(f"course_id LIKE 'course-v1:{org_id}+%'")
# #     condition = "1"
# #     if conditions:
# #         condition = " OR ".join(conditions)
# #
# #     # Note that the "CREATE TEMPORARY TABLE" grant is required to make use of "numbers()" functions.
# #     query = f"""
# # GRANT CREATE TEMPORARY TABLE ON *.* TO {username};
# #
# # GRANT SELECT ON events TO {username};
# # CREATE ROW POLICY OR REPLACE {username} ON events AS RESTRICTIVE FOR SELECT USING {condition} TO {username};
# #
# # GRANT SELECT ON course_grades TO {username};
# # CREATE ROW POLICY OR REPLACE {username} ON course_grades AS RESTRICTIVE FOR SELECT USING {condition} TO {username};
# #
# # GRANT SELECT ON course_enrollments TO {username};
# # CREATE ROW POLICY OR REPLACE {username} ON course_enrollments AS RESTRICTIVE FOR SELECT USING {condition} TO {username};
# #
# # GRANT SELECT ON video_events TO {username};
# # CREATE ROW POLICY OR REPLACE {username} ON video_events AS RESTRICTIVE FOR SELECT USING {condition} TO {username};
# #
# # GRANT SELECT ON video_view_segments TO {username};
# # CREATE ROW POLICY OR REPLACE {username} ON video_view_segments AS RESTRICTIVE FOR SELECT USING {condition} TO {username};
# # """
# #     run_datalake_query(context.root, query)
# #
# #
# # def run_datalake_query(root, query):
# #     config = tutor_config.load(root)
# #     command_secure_opt = "--secure" if config["VISION_CLICKHOUSE_SCHEME"] == "https" else ""
# #     command = f"""clickhouse client \
# #     {command_secure_opt} --host={config["VISION_CLICKHOUSE_HOST"]} --port={config["VISION_CLICKHOUSE_PORT"]} \
# #     --user={config["VISION_CLICKHOUSE_USERNAME"]} \
# #     --password={config["VISION_CLICKHOUSE_PASSWORD"]} \
# #     --database={config["VISION_CLICKHOUSE_DATABASE"]} \
# #     --multiline --multiquery \
# #     --query "{query}"
# #     """
# #     runner = ComposeJobRunner(root, config, local_docker_compose)
# #     runner.run_job("vision-clickhouse", command)
# #
# #
# # @click.group(name="frontend", help="Manage the frontend access")
# # def frontend_command():
# #     pass
# #
# #
# # @click.command(name="createuser", help="Create a new user to access the frontend")
# # @click.option(
# #     "-p",
# #     "--password",
# #     default="",
# #     prompt="User password",
# #     hide_input=True,
# #     confirmation_prompt=True,
# #     help="User password: if undefined you will be prompted to input a password",
# # )
# # @click.option(
# #     "-r",
# #     "--admin",
# #     "is_admin",
# #     is_flag=True,
# #     default=False,
# #     help="Grant root/administration privileges on the frontend to this user",
# # )
# # @click.argument("username")
# # @click.argument("email")
# # @click.pass_obj
# # def frontend_createuser(context, password, is_admin, username, email):
# #     config = tutor_config.load(context.root)
# #     # TODO in case of non-admin, we must define a --role
# #     fab_cmd = "create-admin" if is_admin else "create-user"
# #     command = f"superset fab {fab_cmd} --username {username} --email {email} --password {password}"
# #     runner = ComposeJobRunner(context.root, config, local_docker_compose)
# #     runner.run_job("vision-superset", command)
#
#
# print_command.add_command(print_datalakecreateuser)
# # datalake.add_command(datalake_setpermissions)
# vision_command.add_command(print_command)
# # frontend_command.add_command(frontend_createuser)
# # vision_command.add_command(frontend_command)
