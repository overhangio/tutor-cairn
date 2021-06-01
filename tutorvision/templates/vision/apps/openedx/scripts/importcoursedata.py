import argparse

import requests
from MySQLdb import escape_string as sql_escape_string

import lms.startup

lms.startup.run()

from courseware.courses import get_course
from opaque_keys.edx.keys import CourseKey
from xmodule.modulestore.django import modulestore


def main():
    parser = argparse.ArgumentParser(
        description="Import course block information into the datalake"
    )
    parser.add_argument("-c", "--course-id", action="append", help="Limit import to these courses")
    parser.add_argument("uri", help="Clickhouse URI")
    args = parser.parse_args()

    module_store = modulestore()
    course_ids = args.course_id or []
    for course in module_store.get_courses():
        if str(course.id) in course_ids or not course_ids:
            import_course(course.id, args.uri)


def import_course(course_key, clickhouse_uri):
    course_id = str(course_key)
    # Reload course to fetch all children items
    course = get_course(course_key, depth=None)
    print("======================", course_id, course.display_name)
    values = [
        sql_query(
            "('{}', '{}', '{}', '{}', '{}', '{}')",
            course_id,
            str(child.location),
            child.location.block_id,
            str(position),
            child.display_name,
            full_name,
        )
        for position, (child, full_name) in enumerate(iter_course_blocks(course))
    ]
    if values:
        print(
            f"Inserting {len(values)} items in course_blocks for course '{course_id}'..."
        )
        make_query(
            sql_query(
                "ALTER TABLE course_blocks DELETE WHERE course_id = '{}';",
                course_id,
            ),
            clickhouse_uri,
        )
        insert_query = sql_query(
            "INSERT INTO course_blocks (course_id, block_key, block_id, position, display_name, full_name) VALUES "
        )
        insert_query += ", ".join(values)
        make_query(insert_query, clickhouse_uri)


def iter_course_blocks(item, prefix=""):
    prefix += item.display_name or "N/A"
    yield item, prefix
    prefix += " > "
    for child in item.get_children():
        yield from iter_course_blocks(child, prefix=prefix)


def sql_query(template, *args, **kwargs):
    args = [sql_escape_string(arg).decode() for arg in args]
    kwargs = {key: sql_escape_string(value).decode() for key, value in kwargs.items()}
    return template.format(*args, **kwargs)


def make_query(query, url):
    response = requests.post(url, data=query)
    if response.status_code != 200:
        print(response.content.decode())
        raise ValueError("An error occurred while attempting to post a query")


if __name__ == "__main__":
    main()
