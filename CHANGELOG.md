# Changelog

This file includes a history of past releases. Changes that were not yet added to a release are in the [changelog.d/](./changelog.d) folder.

<!--
⚠️ DO NOT ADD YOUR CHANGES TO THIS FILE! (unless you want to modify existing changelog entries in this file)
Changelog entries are managed by scriv. After you have made some changes to this plugin, create a changelog entry with:

    scriv create

Edit and commit the newly-created file in changelog.d.

If you need to create a new release, create a separate commit just for that. It is important to respect these
instructions, because git commits are used to generate release notes:
  - Modify the version number in `__about__.py`.
  - Collect changelog entries with `scriv collect`
  - The title of the commit should be the same as the new version: "vX.Y.Z".
-->

<!-- scriv-insert-here -->

<a id='changelog-20.0.0'></a>
## v20.0.0 (2025-06-05)

- 💥[Feature] Upgrade to teak. (by @Danyal-Faheem)

<a id='changelog-19.0.4'></a>
## v19.0.4 (2025-04-10)

- [Bugfix] Remove deprecated filter_scopes from import_dashboard script. (by @Danyal-Faheem)

<a id='changelog-19.0.3'></a>
## v19.0.3 (2025-04-03)

- [Bugfix] Migrate to native filters instead of filter box charts on default course overview dashboard which have been completely deprecated as of superset 4.0.0 release. (by @Danyal-Faheem)

- [Improvement] Enable Alerts and Reports in superset. (by @Danyal-Faheem)

- [Improvement] Make superset ports consistent on local and dev by running it on 2247 in both environments. (by @Danyal-Faheem)

<a id='changelog-19.0.2'></a>
## v19.0.2 (2025-03-14)

- [Bugfix] Do not add cairn-postgresql as a dependency when CAIRN_RUN_POSTGRESQL is false. (by @Danyal-Faheem)
- [Bugfix] Add missing CAIRN_POSTGRESQL_HOST and CAIRN_POSTGRESQL_PORT settings to allow usage with external postgresql dbs. (by @Danyal-Faheem)
- [Bugfix] Do not manage cairn-clickhouse permissions CAIRN_RUN_CLICKHOUSE is false. (by @Danyal-Faheem)

<a id='changelog-19.0.1'></a>
## v19.0.1 (2025-03-12)

- [Improvement] Migrate packaging from setup.py/setuptools to pyproject.toml/hatch. (by @Danyal-Faheem)
  - For more details view tutor core PR: https://github.com/overhangio/tutor/pull/1163

- [Improvement] Add hatch_build.py in sdist target to fix the installation issues (by @dawoudsheraz)

<a id='changelog-19.0.0'></a>
## v19.0.0 (2024-10-22)

- [Improvement] Added CORS for embeded Dashboards. (by @Fahadkhalid210)

- [Bugfix] Fix legacy warnings during Docker build. (by @regisb)

- [Improvement] Auto import course structure to clickhouse on course publish by parsing CMS logs. (by @Danyal-Faheem)

- [Feature] Upgrade Clickhouse base image to 24.2.3.70. (by @Danyal-Faheem)

- [Deprecation] Drop support for python 3.8 as it has reached end of life. (by @Danyal-Faheem)

- 💥[Improvement] Rename Tutor's two branches (by @DawoudSheraz):
  * Rename **master** to **release**, as this branch runs the latest official Open edX release tag.
  * Rename **nightly** to **main**, as this branch runs the Open edX master branches, which are the basis for the next Open edX release.

- 💥[Feature] Upgrade to Sumac. (by @Danyal-Faheem)

<a id='changelog-18.0.0'></a>
## v18.0.0 (2024-06-20)

- 💥[Feature] Upgrade to Redwood. (by @Fahadkhalid210)
- [Bugfix] Make plugin compatible with Python 3.12 by removing dependency on `pkg_resources`. (by @regisb)
- [Improvement] Update User Activity dataset query by extending time span to 120 seconds and selecting all events where course ID is not null to improve average time spent in course. (by @Fahadkhalid210)
- [Improvement] Added CORS for embedded Dashboards. (by @Fahadkhalid210)
- 💥[Feature] Upgrade Clickhouse to version 24.1.8.22 and fix query issues due to deprecation of live views. (by @Fahadkhalid210)

<a id='changelog-17.1.0'></a>
## v17.1.0 (2024-02-09)

- 💥[Improvement] Convert `events.user_id` and `video_events.user_id` fields from Int64 to UInt64. (by @FahadKhalid210)
- 💥[[Bugfix] Fix the security context for Vector to ensure it works correctly on Kubernetes. Note that the Vector container will now run in privileged mode. (by @FahadKhalid210)

<a id='changelog-17.0.0'></a>
## v17.0.0 (2023-12-09)

- 💥[Feature] Upgrade to Quince. (by @Fahadkhalid210)
- 💥[Improvement] Convert the `course_blocks.graded` field from String to Boolean. (by @regisb)
- 💥[Improvement] Superset auto_sync roles updated. (by @FahadKhalid210)
- [Improvement] Added Typing to code, Makefile and test action to the repository and formatted code with Black and isort. (by @CodeWithEmad)

<a id='changelog-16.0.3'></a>
## v16.0.3 (2023-09-07)

- [Bugfix] Fix "Error: invalid_request Mismatching redirect URI" - ensure superset respects X-Forwarded-For/X-Forwarded-Proto headers set by Caddy. This effectively fixes running Cairn on HTTPS without a 3rd-party web proxy. (by @ravikhetani)

<a id='changelog-16.0.2'></a>
## v16.0.2 (2023-09-04)

- [Bugfix] Fix "cannot list resource 'pods'" on Kubernetes. (by @regisb)
- [Bugfix] Fix superset database name in user creation with `do cairn-createuser`. (by @regisb)
- [Improvement] Users will now have the access to graded field in course_blocks table with this change which indicates if course unit is graded or not. (by @Faraz32123)

<a id='changelog-16.0.1'></a>
## v16.0.1 (2023-07-17)

- [Bugfix] Fixed user creation command issue with Palm release. (by @jramnai)

<a id='changelog-16.0.0'></a>
## v16.0.0 (2023-06-15)

- 💥[Feature] Upgrade to Palm.
- 💥[Feature] Add single sign-on (SSO) authentication with the LMS. User accounts no longer need to be created manually. Instead, users log in via the LMS and are automatically granted access to their course data. With this change, users will no longer have access to the accounts that were created manually, unless they used the same username in Superset and the LMS. To revert to the previous behaviour, set `CAIRN_ENABLE_SSO=false`. (by @regisb)
    - The `cairn` utility scripts were removed from the Superset and Clickhouse images.
- [Bugfix] Support Superset passwords that include an empty space. (by @regisb)
- [Improvement] Add a scriv-compliant changelog. (by @regisb)

