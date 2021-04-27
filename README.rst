vision plugin for `Tutor <https://docs.tutor.overhang.io>`__
===================================================================================

TODO:
- Collect data with Vector
    - Collect tracking logs
    - Collect nginx logs
    - Send logs to clickhouse
    - Make it optional to mount /var/run/docker.sock
    - adjust vector verbosity
    - log everything to file instead of console? -> tmp volume
- Provision clickhouse
    - make database name a tutor config
    - make clickhouse host a tutor config
    - specify TTL for tables?
    - set permissions for each org:
- Expose data with redash
    - Provision dashboards
    - Custom users
    - Expose grades
    - Reproduce dashboards from https://edx.readthedocs.io/projects/edx-insights/en/latest/Overview.html
    - prevent users from running TRUNCATE from redash
    - frontend user creation:
        - generate random frontend user password in "tutor vision frontend createuser"
        - create root users
        - add delete user command
        - add users to shared openedx organization
- Utility tools for authentication
- Kubernetes compatibility
- Sweet readme

Installation
------------

::

    pip install git+https://github.com/overhangio/tutor-vision

Usage
-----

::

    tutor plugins enable vision
    tutor local quickstart

Create a root user to access the frontend::

    # You will be prompted for your password
    tutor vision frontend createuser --root admin admin@youremail.com

Grant this user access to all data::

    tutor vision datalake createuser admin
    tutor vision datalake setpermissions admin

You can then access the frontend with the user credentials you just created. Open http(s)://vision.<YOUR_LMS_HOST> in your browser. When running locally, this will be http://vision.local.overhang.io.


Management
----------

To add a new, non-admin user::

    # Create a datalake user
    tutor vision datalake createuser yourusername
    # Remember to restrict access, otherwise the new user will have access to everything
    tutor vision datalake setpermissions --course-id 'course-v1:edX+DemoX+Demo_Course' yourusername
    # Create a corresponding user on the frontend
    tutor vision frontend createuser yourusername yourusername@youremail.com

Development
-----------


To reload Vector configuration after changes to vector.toml, run::

    tutor config save && tutor local exec vision-vector sh kill -s HUP

To explore the clickhouse database as root, run::

    tutor local run vision-clickhouse clickhouse-client --host vision-clickhouse \
        --database $(tutor config printvalue VISION_CLICKHOUSE_DATABASE) \
        --user $(tutor config printvalue VISION_CLICKHOUSE_USERNAME) \
        --password $(tutor config printvalue VISION_CLICKHOUSE_PASSWORD)

To launch a Python shell in Redash, run::

    tutor local run vision-redash ./manage.py shell

To backup an existing dashboard, with all its related queries and widgets, first find the dashboard slug from its url. Create a world-writable destination folder::

    mkdir ./dashboards
    chmod a+rwx dashboards

Then run::

    tutor local run -v $(pwd)/dashboards:/tmp/dashboards vision-redash python /redash/scripts/serialize.py dump --output /tmp/dashboards/dashboard.json <your username> <dashboard slug> > ./dashboard.json

You can then re-import this dashboard, for instance to create the same dashboard in another user account::

    tutor local run -v $(pwd)/dashboards:/tmp/dashboards vision-redash python /redash/scripts/serialize.py load /tmp/dashboards/dashboard.json <your username>

License
-------

This software is licensed under the terms of the AGPLv3.
