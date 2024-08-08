import argparse
import json
import os

import requests
# The escape_string was moved to a submodule. It is suggested to use
# `connection.escape_string` instead, but here we don't have a connection object.
# https://mysqlclient.readthedocs.io/user_guide.html#mysql-c-api-function-mapping
from MySQLdb._mysql import escape_string as sql_escape_string

import lms.startup

lms.startup.run()

from lms.djangoapps.courseware.courses import get_course
from xmodule.modulestore.django import modulestore

with open(os.path.join(os.path.dirname(__file__), "..", "clickhouse-auth.json")) as f:
    CLICKHOUSE_AUTH = json.load(f)


def main():
    parser = argparse.ArgumentParser(
        description="Import course block information into the datalake"
    )
    parser.add_argument(
        "-c", "--course-id", action="extend", nargs='*', 
        help="Limit import to these courses"
    )
    args = parser.parse_args()

    module_store = modulestore()
    course_ids = args.course_id or []
    for course in module_store.get_courses():
        if str(course.id) in course_ids or not course_ids:
            import_course(course.id)


def import_course(course_key):
    course_id = str(course_key)
    # Reload course to fetch all children items
    course = get_course(course_key, depth=None)
    print("======================", course_id, course.display_name)
    values = [
        sql_format(
            "('{}', '{}', '{}', '{}', '{}', '{}', {})",
            course_id,
            str(child.location),
            child.location.block_id,
            str(position),
            child.display_name or "N/A",
            full_name,
            "true" if child.graded else "false",
        )
        for position, (child, full_name) in enumerate(iter_course_blocks(course))
    ]
    if values:
        print(
            f"Inserting {len(values)} items in course_blocks for course '{course_id}'..."
        )
        make_query(
            sql_format(
                "ALTER TABLE course_blocks DELETE WHERE course_id = '{}';",
                course_id,
            ),
        )
        insert_query = sql_format(
            "INSERT INTO course_blocks (course_id, block_key, block_id, position, display_name, full_name, graded) VALUES "
        )
        insert_query += ", ".join(values)
        make_query(insert_query)


def iter_course_blocks(item, prefix=""):
    prefix += item.display_name or "N/A"
    yield item, prefix
    prefix += " > "
    for child in item.get_children():
        yield from iter_course_blocks(child, prefix=prefix)


def sql_format(template, *args, **kwargs):
    args = [sql_escape_string(arg).decode() for arg in args]
    kwargs = {key: sql_escape_string(value).decode() for key, value in kwargs.items()}
    return template.format(*args, **kwargs)


def make_query(query):
    clickhouse_uri = (
        f"{CLICKHOUSE_AUTH['http_scheme']}://{CLICKHOUSE_AUTH['username']}:{CLICKHOUSE_AUTH['password']}@"
        f"{CLICKHOUSE_AUTH['host']}:{CLICKHOUSE_AUTH['http_port']}/?database={CLICKHOUSE_AUTH['database']}"
    )
    response = requests.post(clickhouse_uri, data=query.encode("utf8"))
    if response.status_code != 200:
        print(response.content.decode())
        raise ValueError("An error occurred while attempting to post a query")


if __name__ == "__main__":
    main()
