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

