#! /usr/bin/env python3

import argparse
import json
from time import time

from superset.app import create_app

app = create_app()
app.app_context().push()

from superset.connectors.sqla.models import SqlaTable
from superset.models.core import Database
from superset.models.slice import Slice
from superset.extensions import db, security_manager
import superset.commands.dashboard.importers.v0 as importers
from werkzeug.security import generate_password_hash

# Our convenient library
from superset.cairn import bootstrap as cairn_bootstrap


now = time()


def main():
    parser = argparse.ArgumentParser(
        description="Bootstrap user creation and dashboards"
    )
    subparsers = parser.add_subparsers()

    # Create user
    parser_user = subparsers.add_parser("createuser", help="Create or update user")
    parser_user.add_argument(
        "-d",
        "--db",
        "--database",
        help=(
            "Name of the Superset database to which the user should be granted access."
            " Defaults to the username."
        ),
    )
    parser_user.add_argument(
        "--admin",
        action="store_true",
        help=("Make the user an administrator."),
    )
    parser_user.add_argument(
        "-p",
        "--password",
        help="User password.",
    )
    parser_user.add_argument(
        "--firstname", default="", help="User first name (optional)."
    )
    parser_user.add_argument(
        "--lastname", default="", help="User last name (optional)."
    )
    parser_user.add_argument(
        "-c",
        "--course-id",
        action="append",
        help="Restrict user to access data only from these courses.",
    )
    parser_user.add_argument("username")
    parser_user.add_argument("email")
    parser_user.set_defaults(func=bootstrap_user)

    # Bootstrap dashboards
    parser_dashboards = subparsers.add_parser(
        "bootstrap-dashboards",
        help="Bootstrap datasets and dashboards for a given user",
    )
    parser_dashboards.add_argument(
        "-d",
        "--db",
        "--database",
        help=(
            "Name of the Superset database to which the objects should be linked."
            " By default, this will be the 'openedx-<username>'."
        ),
    )
    parser_dashboards.add_argument("username")
    parser_dashboards.add_argument("path", nargs="+")
    parser_dashboards.set_defaults(func=bootstrap_dashboards)

    args = parser.parse_args()
    args.func(args)


# Note: we'd like to get rid of this command by relying on `superset fab create-user`
# but the "create-user" command fails if the user already exists.
def bootstrap_user(args):
    # Bootstrap database
    database_name = args.db or f"openedx-{args.username}"
    cairn_bootstrap.create_superset_db(args.username, database_name)

    # Get or create user
    user = security_manager.find_user(args.username)
    if user:
        print(f"User '{args.username}' already exists. Skipping creation.")
    else:
        print(f"Creating user '{args.username}'...")
        user = security_manager.add_user(
            args.username,
            args.firstname,
            args.lastname,
            args.email,
            security_manager.find_role("Gamma"),
        )
        if user is None or user is False:
            # This may happen for instance when the email address is already associated
            # to a different username
            raise RuntimeError(
                f"Failed to create user '{args.username}' email='{args.email}'"
            )

    # Set password
    if args.password:
        print("Setting user password...")
        user.password = generate_password_hash(args.password)
        db.session.add(user)
        db.session.commit()

    # Create user role, clickhouse db, etc.
    cairn_bootstrap.setup_user(args.username, course_ids=args.course_id)

    # Associate user to roles
    user_roles = cairn_bootstrap.get_role_names(args.username)
    if args.admin:
        user_roles.append("Admin")
    for role_name in user_roles:
        role = security_manager.find_role(role_name)
        if role in user.roles:
            print(f"Role '{role_name}' is already associated to user.")
        else:
            print(f"Associating role '{role_name}' to user...")
            user.roles.append(role)
            db.session.add(user)
            db.session.commit()

    print("Done.")


# Note: we would like to start using superset's native export/import-dashboards command
# but we failed to get it to work.
def bootstrap_dashboards(args):
    database_name = args.db or args.username
    database = load_database(database_name)
    user = load_user(args.username)

    for path in args.path:
        print(
            f"importing dashboard {path} for user='{user.username}' db='{database.database_name}'... "
        )
        dashboard = load_dashboard_file(path)
        import_dashboard(dashboard, user, database)


def load_database(database_name):
    return (
        db.session.query(Database).filter(Database.database_name == database_name).one()
    )


def load_user(username):
    return (
        db.session.query(security_manager.user_model)
        .filter(security_manager.user_model.username == username)
        .one()
    )


def load_dashboard_file(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f, object_hook=importers.decode_dashboards)


def import_dashboard(data, user, database):
    # Load datasets
    for dataset in data["datasources"]:
        dataset.params = "{}"
        # This should overwrite the existing dataset, if any with the same name
        new_dataset_id = importers.import_dataset(dataset, database.id, now)
        new_dataset = db.session.query(SqlaTable).get(new_dataset_id)
        # Make current user the new owner
        new_dataset.owners.append(user)
        db.session.add(new_dataset)

    for dashboard in data["dashboards"]:
        # Load slices
        new_slices = []
        slices = dashboard.slices[:]
        old_to_new_slice_id_map = {}

        for dashboard_slice in slices:
            # Make sure the new slice does not point to the old slice
            params_dict = dashboard_slice.params_dict
            params_dict["database_name"] = database.name
            params_dict.pop("remote_id")
            dashboard_slice.params = json.dumps(params_dict)
            old_slice_id = dashboard_slice.id
            dashboard_slice.id = None
            # Create new slice
            new_slice_id = importers.import_chart(dashboard_slice, None, now)
            new_slice = db.session.query(Slice).get(new_slice_id)
            old_to_new_slice_id_map[old_slice_id] = new_slice_id
            # Make current user the new owner
            new_slice.owners.append(user)
            new_slices.append(new_slice)
            db.session.add(new_slice)

        # Add slices to dashboard
        dashboard.slices = new_slices
        # Set dashboard owner
        dashboard.owners.append(user)
        # Update position JSON
        position = dashboard.position.copy()
        for chart in position.values():
            if (
                "meta" in chart
                and isinstance(chart["meta"], dict)
                and "chartId" in chart["meta"]
            ):
                chart["meta"]["chartId"] = old_to_new_slice_id_map[
                    chart["meta"]["chartId"]
                ]
        dashboard.position_json = json.dumps(position)

        # Update filter mapping
        metadata = json.loads(dashboard.json_metadata)
        dashboard.json_metadata = json.dumps(metadata)

        # Load dashboard
        db.session.add(dashboard)

        # Commit changes
        db.session.commit()


if __name__ == "__main__":
    main()
