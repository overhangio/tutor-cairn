Tutor Vision: scalable, real-time analytics for Open edX
========================================================

TODO: Sweet readme

Installation
------------

::

    tutor license install tutor-vision

Usage
-----

::

    tutor plugins enable vision
    tutor local quickstart

Create an admin user to access the frontend::

    # You will be prompted for a new password
    tutor local run vision-superset superset fab create-admin --username yourusername --email user@example.com

You can then access the frontend with the user credentials you just created. Open http(s)://vision.<YOUR_LMS_HOST> in your browser. When running locally, this will be http://vision.local.overhang.io. The admin user will automatically be granted access to the "openedx" database in Superset and will be able to query all tables.

Management
----------

Most of your users should probably not have access to all data from all courses. To restrict a given user to one or more courses or organizations, select the course IDs and/or organization IDS to which the user should have access and create a user with limited access to the datalake::

    tutor local run vision-clickhouse vision createuser --course-id='course-v1:edX+DemoX+Demo_Course' --org-id='edX' yourusername

Then, create the corresponding user on the frontend::

    tutor local run vision-superset vision createuser yourusername yourusername@youremail.com

Your frontend user will automatically be associated to the datalake database you created, provided they share the same name.

Vision comes with a convenient pre-built dashboard that you can add to any user account::

    tutor local run vision-superset vision bootstrap-dashboards yourusername /app/bootstrap/courseoverview.json

Course block IDs and names are loaded from the Open edX modulestore into the datalake. After making changes to your course, you might want to refresh the course structure stored in the datalake. To do so, run::

    tutor local init --limit=vision

Or, if you want to avoid running the full plugin initialization::

    tutor local run \
        -v $(tutor config printroot)/env/plugins/vision/apps/openedx/scripts/:/openedx/scripts \
        -v $(tutor config printroot)/env/plugins/vision/apps/clickhouse/auth.json:/openedx/clickhouse-auth.json \
        lms python /openedx/scripts/importcoursedata.py

When running on Kubernetes instead of locally, most commands above can be re-written with `tutor k8s exec service "command"` instead of `tutor local run service command`. For instance::

    # Privileved user creation
    tutor k8s exec vision-superset "superset fab create-admin --username yourusername --email user@example.com"
    # Unprivileged user creation
    tutor k8s exec vision-clickhouse "vision createuser --course-id='course-v1:edX+DemoX+Demo_Course' --org-id='edX' yourusername"
    tutor k8s exec vision-superset "vision createuser yourusername yourusername@youremail.com"

Development
-----------


To reload Vector configuration after changes to vector.toml, run::

    tutor config save && tutor local exec vision-vector sh -c "kill -s HUP 1"

To explore the clickhouse database as root, run::

    tutor local run vision-clickhouse vision client

To launch a Python shell in Superset, run::

    tutor local run vision-superset superset shell


License
-------

This software is licensed under the terms of the AGPLv3.
