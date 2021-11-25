Cairn: scalable, real-time analytics for Open edX
==================================================

Analytics are an essential component of an online learning platform: you need to know whether your courses are effective and which parts need some improvement. You need to know if your students are falling by, and if they do, you need to detect the early warning signs. When your courses are successful, you want to get periodical engagement reports.

We created a tool to help you answer all these questions. Cairn is a Tutor plugin that you install on top of an Open edX platform and that gives you access to a powerful, full-blown analytics stack. Cairn comes with the following features out of the box:

🖴 **Unified datalake of learner events and stateful data**: both learner-triggered events, coming from the Open edX tracking logs, and stateful data, coming from the existing databases, are available for querying in a single unified interface. This means that you can, for instance, query the grades of the students that visited your platform in the past 24 hours, or collect the email addresses of the students who did not yet complete the latest assignment.

⚡﻿ **Real-time:** new events are visible immediately in your analytics interface. No more waiting for slow batch jobs to complete!

🔑 **Course- and org-based data access rights:** your course staff is granted access only to the data rows that concern them. Cairn makes it easy to create new users with granular access permissions.

🎁 **Working dashboards out of the box:** Cairn comes with a fully functional dashboard that you can start playing with right away.

🛠️ **Fully customizable data and dashboards:** your data scientists, business intelligence team and other tinkerers can freely explore your course data, create and share their own queries, datasets and dashboards. All it takes is a little bit of SQL.

🚀 **Scalable:** Cairn scales as much as its backend, which was designed for Internet scale.

Cairn vs alternatives
---------------------

========================================== =====  ===================================================================================  ===================================================
List of features                           Cairn  `Open edX Insights <https://edx.readthedocs.io/projects/edx-insights/en/latest/>`__  `Figures <https://github.com/appsembler/figures>`__
========================================== =====  ===================================================================================  ===================================================
Event aggregation                            ✅      ✅                                                                                    ❌
Real-time data                               ✅      ❌                                                                                    ✅
Easy to install                              ✅      ❌                                                                                    ✅
Custom queries and dashboards                ✅      ❌                                                                                    ❌
Works with the latest Open edX versions      ✅      ✅                                                                                    ❌
========================================== =====  ===================================================================================  ===================================================


How does Cairn work?
--------------------

Cairn uses the same collect/store/expose paradigm made popular by other frameworks such as the `ELK Stack <https://www.elastic.co/fr/elastic-stack>`__ -- excepts that all the components are different and better suited to Open edX:

- On the server side, tracking logs are collected by `Vector <https://vector.dev/>`__, an efficient, cloud-native log collector.
- Tracking log events are then stored in a `Clickhouse <https://clickhouse.tech/>`__ table, which is the cornerstone of Cairn. Clickhouse also exposes MySQL data via live and materialized views. This is the magic piece of the puzzle which allows us to join event and MySQL data.
- The data inside Clickhouse is made visible to the end-users in a `Superset <https://superset.apache.org/>`__ frontend.

Installation
------------

Cairn requires a `Tutor Wizard Edition license <https://overhang.io/tutor/wizardedition>`__. Once you have enabled your license, installing the plugin is as simple as running::

    tutor license install tutor-cairn

Usage
-----

Getting started
~~~~~~~~~~~~~~~

Enable the plugin with::

    tutor plugins enable cairn

Then, restart your platform and run the initialization scripts::

    tutor local quickstart

Create credentials to access the Clickhouse database::

    tutor local run cairn-clickhouse cairn createuser YOURUSERNAME

Create an admin user to access the frontend::

    # You will be prompted for a new password
    tutor local run cairn-superset cairn createuser --admin YOURUSERNAME YOURUSERNAME@YOUREMAIL.COM

You can then access the frontend with the user credentials you just created. Open http(s)://data.<YOUR_LMS_HOST> in your browser. When running locally, this will be http://data.local.overhang.io. The admin user will automatically be granted access to the "openedx" database in Superset and will be able to query all tables.

To import the "Course overview" dashboard that comes with Cairn, run::

    tutor local run cairn-superset cairn bootstrap-dashboards YOURUSERNAME /app/bootstrap/courseoverview.json

Some event data will be missing from your dashboards: just start using your LMS and refresh your dashboard. The new events should appear immediately.

.. image:: https://overhang.io/static/catalog/img/cairn/courseoverview-01.png
    :alt: Course overview dashboard part 1
.. image:: https://overhang.io/static/catalog/img/cairn/courseoverview-02.png
    :alt: Course overview dashboard part 2
.. image:: https://overhang.io/static/catalog/img/cairn/courseoverview-03.png
    :alt: Course overview dashboard part 3

Data-based access control
~~~~~~~~~~~~~~~~~~~~~~~~~

Most of your users should probably not have access to all data from all courses. To restrict a given user to one or more courses or organizations, select the course IDs and/or organization IDS to which the user should have access and create a user with limited access to the datalake::

    tutor local run cairn-clickhouse cairn createuser --course-id='course-v1:edX+DemoX+Demo_Course' --org-id='edX' YOURUSERNAME

Then, create the corresponding user on the frontend with the same command as above (but without the ``--admin`` option)::

    tutor local run cairn-superset cairn createuser YOURUSERNAME YOURUSERNAME@YOUREMAIL.COM

Your frontend user will automatically be associated to the datalake database you created.

Refreshing course block data
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Course block IDs and names are loaded from the Open edX modulestore into the datalake. After making changes to your course, you might want to refresh the course structure stored in the datalake. To do so, run::

    tutor local init --limit=cairn

Or, if you want to avoid running the full plugin initialization::

    tutor local run \
        -v $(tutor config printroot)/env/plugins/cairn/apps/openedx/scripts/:/openedx/scripts \
        -v $(tutor config printroot)/env/plugins/cairn/apps/clickhouse/auth.json:/openedx/clickhouse-auth.json \
        lms python /openedx/scripts/importcoursedata.py

Running on Kubernetes
~~~~~~~~~~~~~~~~~~~~~

When running on Kubernetes instead of locally, most commands above can be re-written with `tutor k8s exec service "command"` instead of `tutor local run service command`. For instance::

    # Privileged user creation
    tutor k8s exec cairn-superset "superset fab create-admin --username YOURUSERNAME --email user@example.com"
    # Unprivileged user creation
    tutor k8s exec cairn-clickhouse "cairn createuser --course-id='course-v1:edX+DemoX+Demo_Course' --org-id='edX' YOURUSERNAME"
    tutor k8s exec cairn-superset "cairn createuser YOURUSERNAME YOURUSERNAME@YOUREMAIL.COM"

Collecting past events
~~~~~~~~~~~~~~~~~~~~~~

When Cairn is launched for the first time, past events that were triggered prior to the plugin installation will not be loaded in the data lake. If you are interested in loading past events, you should load them manually by running::

    tutor local start -d cairn-clickhouse
    tutor local run \
      --volume="$(tutor config printroot)/data/lms/logs/:/var/log/openedx/:ro" \
      --volume="$(tutor config printroot)/env/plugins/cairn/apps/vector/file.toml:/etc/vector/file.toml:ro" \
      -e VECTOR_CONFIG=/etc/vector/file.toml cairn-vector

The latter command will parse tracking log events from the ``$(tutor config printroot)/data/lms/logs/tracking.log`` file that contains all the tracking logs since the creation of your platform. The command will take a while to run if you have a large platform that has been running for a long time. It can be interrupted at any time and started again, as the log collector keeps track of its position within the tracking log file.

Adding data to your data lake
-----------------------------

Tables created in Clickhouse are managed by a lightweight migration system. You can view existing migrations that ship by default with Cairn in the following folder: ``$VIRTUAL_ENV/lib/python3.8/site-packages/tutorcairn/templates/cairn/apps/clickhouse/migrations.d/``.

You are free to create your own migrations that will automatically be created in Clickhouse every time the ``tutor local quickstart`` or ``tutor local init`` commands are run. To do so, as usual in Tutor, you should create a `Tutor plugin <https://docs.tutor.overhang.io/plugins.html>`__. This plugin should include the ``CAIRN_MIGRATIONS_FOLDER`` configuration. This setting should point to a template folder, inside the plugin, where migration templates are defined. For instance, assuming you created the "customcairn" plugin::

    config = {
        "defaults": {
            "CAIRN_MIGRATIONS_FOLDER": "customcairn/apps/migrations.d"
        }
    }

In this example, the following folder should be created in the plugin:: ``tutorcustomcairn/templates/customcairn/apps/migrations.d/``. Then, you should add your migration files there. Migrations will be applied in alphabetical order whenever you run ``tutor local quickstart`` or ``tutor local init``.

Development
-----------

To reload Vector configuration after changes to vector.toml, run::

    tutor config save && tutor local exec cairn-vector sh -c "kill -s HUP 1"

To explore the clickhouse database as root, run::

    tutor local run cairn-clickhouse cairn client

To launch a Python shell in Superset, run::

    tutor local run cairn-superset superset shell

.. image:: https://overhang.io/static/catalog/img/cairn.png
    :alt: Alpine cairn

Support
-------

Are you having trouble with Cairn? Do you have questions about this plugin? Please get in touch with us at contact@overhang.io. Community support is also available on the official Tutor forums: https://discuss.overhang.io

License
-------

This software is licensed under the terms of the AGPLv3.
