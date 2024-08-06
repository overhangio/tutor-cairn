from aiohttp import web
import subprocess
from opaque_keys.edx.locator import CourseLocator

async def import_course_to_clickhouse(request):

    data = await request.json()
    
    if not isinstance(data, list) or 'course_id' not in data[0]:
        return web.json_response({"error":"Value course_id is required."}, status=400)
    
    course_id = data[0]['course_id']
    
    # Verify course_id is a valid course_id
    try:
        CourseLocator.from_string(course_id)
    except:
        return web.json_response({"error": "Invalid course_id"}, status=400)
    
    try:
        subprocess.run(["python", "/openedx/scripts/importcoursedata.py", "-c", course_id])
        return web.json_response({"result": "success"}, status=200)
    except Exception as e:
        return web.json_response({'error': str(e)}, status=400)

app = web.Application()
app.router.add_post('/import_course/', import_course_to_clickhouse)

web.run_app(app, host='0.0.0.0', port=9282)
