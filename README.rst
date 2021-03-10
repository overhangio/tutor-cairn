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
- Expose data with redash
- Provision dashboards
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

To access the analytics frontend, open http(s)://vision.<YOUR_LMS_HOST> in your browser. When running locally, this will be http://vision.local.overhang.io. The email address and password required for logging in are::

    tutor config printvalue VISION_REDASH_ROOT_EMAIL
    tutor config printvalue VISION_REDASH_ROOT_PASSWORD

Development
-----------

To reload Vector configuration after changes to vector.toml, run::

    tutor config save && tutor local exec vision-vector sh kill -s HUP

License
-------

This software is licensed under the terms of the AGPLv3.