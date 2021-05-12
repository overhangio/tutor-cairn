#! /usr/bin/env python3

import argparse
from getpass import getpass
import os

from redash import create_app
from redash import models
from redash.query_runner.clickhouse import ClickHouse
from redash.utils.configuration import ConfigurationContainer


def main():
    parser = argparse.ArgumentParser(
        description="Create a Redash user with the corresponding data source pointing to Clickhouse"
    )
    parser.add_argument("-r", "--root", action="store_true", help="Make a root user")
    parser.add_argument(
        "-p", "--password", help="If undefined, you will be prompted for a password"
    )
    parser.add_argument("username")
    parser.add_argument("email")
    args = parser.parse_args()

    app = create_app()
    app.app_context().push()

    password = args.password
    while not password:
        password = getpass(prompt="User password: ")

    org = get_default_org()
    group = get_group(org, args.username, is_root=args.root)
    user = get_user(org, group, args.username, args.email, password, is_root=args.root)
    get_datasource(org, group, user.name)


def get_default_org():
    org_slug = "default"
    org = models.Organization.get_by_slug(org_slug)
    if org:
        print("Org already exists")
    else:
        print("Creating org...")
        org = models.Organization(
            name=org_slug, slug=org_slug, settings={"beacon_consent": False}
        )
        models.db.session.add(org)
        models.db.session.commit()

    # Get org admin group
    if org.admin_group:
        print("Org admin group already exists")
    else:
        print("Creating org admin group...")
        admin_group = models.Group(
            name="admin",
            permissions=["admin", "super_admin"],
            org=org,
            type=models.Group.BUILTIN_GROUP,
        )
        models.db.session.add_all([org, admin_group])
        models.db.session.commit()

    return org


def get_group(org, username, is_root=False):
    group = models.Group.query.filter(
        models.Group.name == username, models.Group.org == org
    ).first()
    if group:
        print("Group '{}' already exists".format(username))
    else:
        excluded_permissions = [] if is_root else ["list_users"]
        permissions = [
            permission
            for permission in models.Group.DEFAULT_PERMISSIONS
            if permission not in excluded_permissions
        ]
        group = models.Group(name=username, org=org, permissions=permissions)
        models.db.session.add(group)
        models.db.session.commit()
        print("Created group '{}'".format(group.name))
    if is_root:
        for permission in ["admin", "super_admin"]:
            if permission not in group.permissions:
                print("Adding permission '{}' to group".format(permission))
                group.permissions.append(permission)
        models.db.session.add(group)
        models.db.session.commit()
    return group


def get_user(org, group, username, email, password, is_root=False):
    user = models.User.query.filter(models.User.email == email).first()
    if user:
        print("User already exists")
    else:
        user = models.User(org=org, email=email, name=username, group_ids=[group.id])
        print("Created user '{}/{}'".format(user.email, user.name))
    user.hash_password(password)
    models.db.session.add(user)
    models.db.session.commit()
    if is_root:
        if org.admin_group.id in user.group_ids:
            print("User is already in admin group")
        else:
            print("Adding user to admin group...")
            user.group_ids = user.group_ids + [org.admin_group.id]
            models.db.session.add(user)
            models.db.session.commit()
    return user


def get_datasource(org, group, username):
    # Get or create datasource
    options = ConfigurationContainer(
        {
            "url": "{}://{}:{}".format(
                os.environ["CLICKHOUSE_SCHEME"],
                os.environ["CLICKHOUSE_HOST"],
                os.environ["CLICKHOUSE_PORT"],
            ),
            "user": username,
            "password": "",
            "dbname": os.environ["CLICKHOUSE_DATABASE"],
        },
        ClickHouse.configuration_schema(),
    )
    data_source = models.DataSource.query.filter(
        models.DataSource.name == username
    ).first()
    if data_source:
        print("Data source already exists")
    else:
        data_source = models.DataSource(
            name=username,
            type="clickhouse",
            options=options,
            org=org,
        )
        data_source_group = models.DataSourceGroup(data_source=data_source, group=group)
        models.db.session.add_all([data_source, data_source_group])
        models.db.session.commit()
        print("Created datasource '{}'".format(data_source.name))


if __name__ == "__main__":
    main()
