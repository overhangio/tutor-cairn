import lms.startup

lms.startup.run()

from xmodule.modulestore.django import modulestore
from opaque_keys.edx.keys import CourseKey
from courseware.courses import get_course


def main():
    module_store = modulestore()
    for course in module_store.get_courses():
        course_id = course.id.html_id()
        course_key = CourseKey.from_string(course_id)
        course = get_course(course_key, depth=None)
        for position, child in enumerate(iter_children(course)):
            print(course.display_name, position, child.location.block_id, child.display_name)


def iter_children(item):
    yield item
    for child in item.get_children():
        yield from iter_children(child)


if __name__ == "__main__":
    main()
