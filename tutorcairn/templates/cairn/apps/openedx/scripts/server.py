"""
This module provides an HTTP service for importing course data into ClickHouse.

It defines a single HTTP endpoint that allows for the submission of course IDs,
which are then processed and used to trigger a subprocess for data import.

Functions:
- import_courses_to_clickhouse(request): Handles POST requests to '/courses/published/'.
  Validates the input data, verifies course IDs, and triggers an external Python script
  to import the data into ClickHouse.

Usage:
- python server.py
- Run this module to start the HTTP server. It listens on port 9282 and processes
  requests sent to the '/courses/published/' endpoint.
"""
import logging
import subprocess

from aiohttp import web
from opaque_keys.edx.locator import CourseLocator

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

log = logging.getLogger(__name__)

async def import_courses_to_clickhouse(request):

    data = await request.json()
    if not isinstance(data, list):
        return web.json_response({"error": f"Incorrect data format. Expected list, got {data.__class__}."}, status=400)
    course_ids = []
    for course in data:
        course_id = course.get("course_id")
        if not isinstance(course_id, str):
            return web.json_response({"error": f"Incorrect course_id format. Expected str, got {course_id.__class__}."}, status=400)
        
    # Get the list of unique course_ids
    unique_courses = list({course['course_id']: course for course in data}.values())

    course_ids = []

    for course in unique_courses:
        course_id = course['course_id']
        # Verify course_id is a valid course_id
        try:
            CourseLocator.from_string(course_id)
        except Exception as e:
            log.exception(f"An error occured: {str(e)}")
            return web.json_response({"error": f"Incorrect arguments. Expected valid course_id, got {course_id}."}, status=400)

        course_ids.append(course_id)

    subprocess.run(["python", "/openedx/scripts/importcoursedata.py", "-c", *course_ids], check=True)
    return web.Response(status=204)
    

app = web.Application()
app.router.add_post('/courses/published/', import_courses_to_clickhouse)

web.run_app(app, host='0.0.0.0', port=9282)
