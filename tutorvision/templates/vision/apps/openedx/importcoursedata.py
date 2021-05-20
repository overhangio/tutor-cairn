import urllib.request
import urllib.parse

import lms.startup

lms.startup.run()

from courseware.courses import get_course
from MySQLdb import escape_string as sql_escape_string
from opaque_keys.edx.keys import CourseKey
from xmodule.modulestore.django import modulestore

# TODO actually run this script during init by mounting inside the lms container
def main():
    module_store = modulestore()
    for course in module_store.get_courses():
        import_course(course.id)


def import_course(course_key):
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
            )
        )
        insert_query = sql_query(
            "INSERT INTO course_blocks (course_id, block_key, block_id, position, display_name, full_name) VALUES "
        )
        insert_query += ", ".join(values)
        make_query(insert_query)


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


def make_query(query):
    # TODO pass connection strings
    url = "http://vision-clickhouse:8123/?%s" % urllib.parse.urlencode(
        {"database": "openedx"}
    )
    try:
        urllib.request.urlopen(url, data=query.encode())
    except urllib.request.HTTPError as e:
        print(e.read().decode())
        raise


if __name__ == "__main__":
    main()
