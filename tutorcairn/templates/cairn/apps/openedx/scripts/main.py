import subprocess
from fastapi import FastAPI, Request

app = FastAPI()

@app.post("/import_course/")
async def import_course_to_clickhouse(request: Request):
    response = await request.json()
    course_id = response[0]['course_id']
    # We use a subprocess here as the modulestore data is cached and the
    # script tries to insert the same number of blocks everytime
    subprocess.call(["python", "/openedx/scripts/importcoursedata.py", "-c", course_id])
    return({"result": "success"})
