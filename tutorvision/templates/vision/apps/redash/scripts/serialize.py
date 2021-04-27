import argparse
from datetime import datetime
import json

from redash import create_app
from redash import models
from redash.models.users import Group, User
from redash import serializers


def main():
    parser = argparse.ArgumentParser(
        description="Dump a dashboard to JSON, along with all associated widgets, queries and visualizations"
    )
    subparsers = parser.add_subparsers()

    # Dump command
    dump_command = subparsers.add_parser("dump", help="Dump objects to JSON")
    dump_command.set_defaults(func=dump)
    dump_command.add_argument(
        "-o",
        "--output",
        default="-",
        help="Destination file. Leave to '-' to print in stdout",
    )
    dump_command.add_argument("username")
    dump_command.add_argument("slug")

    # Load command
    load_command = subparsers.add_parser("load", help="Load objects from JSON")
    load_command.set_defaults(func=load)
    load_command.add_argument(
        "-n",
        "--dry-run",
        action="store_true",
        help="Do not actually commit changes (good for debugging)",
    )
    load_command.add_argument(
        "-s",
        "--skip-existing",
        action="store_true",
        help="Do not actually create objects when an object with identical name already exists",
    )
    load_command.add_argument(
        "-d",
        "--datasource",
        help="Assign queries to the specified datasource. If undefined, queries will be associated to the first datasource of the first user group.",
    )
    load_command.add_argument(
        "path",
        help="JSON-formatted file to load data from",
    )
    load_command.add_argument("username", help="Add dashboard to this user account")

    app = create_app()
    app.app_context().push()

    args = parser.parse_args()
    args.func(args)


def dump(args):
    user = get_user(args.username)
    dashboard = get_dashboard(user, args.slug)
    data = serialize(dashboard)
    data = clean_data(data)
    serialized = json.dumps(data, sort_keys=True, indent=2)
    save_to(serialized, args.output)


def load(args):
    with open(args.path) as f:
        serialized = json.load(f)

    deserializer = Deserializer(
        args.username,
        data_source_id=args.datasource,
        dry_run=args.dry_run,
        skip_existing=args.skip_existing,
    )
    deserializer.deserialize_dashboard(serialized)


class Deserializer:
    def __init__(
        self, username, data_source_id=None, dry_run=False, skip_existing=False
    ):
        self.user = get_user(username)
        self.data_source_id = data_source_id
        if not self.data_source_id:
            group = Group.query.get(self.user.group_ids[0])
            self.data_source_id = group.data_sources[0].data_source.id
        print(
            "Objects will be associated to datasource #{}".format(self.data_source_id)
        )

        self.dry_run = dry_run
        self.skip_existing = skip_existing
        self.widget_id_map = {}
        self.visualization_id_map = {}
        self.query_id_map = {}

    def deserialize_dashboard(self, params):
        print("--- Creating dashboard '{}'...".format(params["name"]))
        dashboard = models.Dashboard(
            user=self.user,
            org=self.user.org,
            name=params["name"],
            layout=[],
            is_draft=False,
        )
        models.db.session.add(dashboard)

        for widget in params["widgets"]:
            visualization = widget["visualization"]
            self.deserialize_query(visualization["query"])
            self.deserialize_visualization(visualization)
            self.deserialize_widget(dashboard.id, widget)

        if self.dry_run:
            print("Dry-run mode: changes are discarded.")
        else:
            models.db.session.commit()

    def deserialize_query(self, params):
        old_id = params["id"]
        if old_id in self.query_id_map:
            return

        if self.skip_existing:
            existing_query = models.Query.query.filter(
                models.Query.user == self.user, models.Query.name == params["name"]
            ).first()
            if existing_query:
                print(
                    "--- Skipping creation of query '{}' which already exists".format(
                        params["name"]
                    )
                )
                self.query_id_map[old_id] = existing_query.id
                return

        print("--- Creating query '{}'...".format(params["name"]))
        # If there are parameter queries, create these first
        for parameter in params["options"]["parameters"]:
            if "query" in parameter:
                parameter_query_params = parameter.pop("query")
                self.deserialize_query(parameter_query_params)
                parameter["queryId"] = self.query_id_map[parameter_query_params["id"]]

        query = models.Query(
            user=self.user,
            org=self.user.org,
            data_source_id=self.data_source_id,
            **project_all_but(params, ["id"])
        )
        models.db.session.add(query)
        self.query_id_map[old_id] = query.id

    def deserialize_visualization(self, params):
        old_id = params["id"]
        if old_id in self.visualization_id_map:
            return

        query_id = self.query_id_map[params["query"]["id"]]
        if self.skip_existing:
            existing_visualization = (
                models.Visualization.query.join(models.Query)
                .filter(
                    models.Visualization.query_id == query_id,
                    models.Query.user == self.user,
                    models.Visualization.name == params["name"],
                )
                .first()
            )
            if existing_visualization:
                print(
                    "--- Skipping creation of visualization '{}' which already exists".format(
                        params["name"]
                    )
                )
                self.visualization_id_map[old_id] = existing_visualization.id
                return

        print("--- Creating visualization '{}'...".format(params["name"]))
        options = json.dumps(params["options"])
        visualization = models.Visualization(
            query_id=query_id,
            options=options,
            **project_all_but(params, ["id", "options", "query"])
        )
        models.db.session.add(visualization)
        self.visualization_id_map[old_id] = visualization.id

    def deserialize_widget(self, dashboard_id, params):
        old_id = params["id"]
        if old_id in self.widget_id_map:
            return
        print("--- Creating widget...")

        widget = models.Widget(
            visualization_id=self.visualization_id_map[params["visualization"]["id"]],
            dashboard_id=dashboard_id,
            options=json.dumps(params["options"]),
            **project_all_but(params, ["id", "options", "visualization"])
        )
        models.db.session.add(widget)
        self.widget_id_map[old_id] = widget.id


def get_user(username):
    org = models.Organization.get_by_slug("default")
    return org.users.filter(User.name == username).one()


def get_dashboard(user, slug):
    return models.Dashboard.query.filter(
        models.Dashboard.user == user, models.Dashboard.slug == slug
    ).one()


def serialize(dashboard):
    return {
        "id": dashboard.id,
        "name": dashboard.name,
        "widgets": [serialize_widget(w) for w in dashboard.widgets],
    }


def serialize_widget(widget):
    """
    TODO don't include draft or achived queries.
    """
    widget_fields = set(["id", "width", "options", "text", "visualization"])
    visualization_fields = set(
        ["id", "type", "name", "description", "options", "query"]
    )
    query_fields = set(
        ["id", "name", "description", "query_text", "schedule", "options"]
    )
    serialized = serializers.serialize_widget(widget)
    serialized = project(serialized, widget_fields)
    if "visualization" in serialized:
        serialized["visualization"] = project(
            serialized["visualization"], visualization_fields
        )
        # Convert 'query.query' field to 'query.query_text'
        serialized["visualization"]["query"]["query_text"] = serialized[
            "visualization"
        ]["query"]["query"]
        # If query depends on some other parameter, save this other query, too
        for parameter in serialized["visualization"]["query"]["options"]["parameters"]:
            if "queryId" in parameter:
                parameter_query = models.Query.query.get(parameter.pop("queryId"))
                parameter["query"] = serializers.serialize_query(parameter_query)
                # don't forget to convert query to query_text
                parameter["query"]["query_text"] = parameter["query"]["query"]
                parameter["query"] = project(parameter["query"], query_fields)
        serialized["visualization"]["query"] = project(
            serialized["visualization"]["query"], query_fields
        )
    return serialized


def project(data, allowed_keys):
    return {key: value for key, value in data.items() if key in allowed_keys}


def project_all_but(data, excluded_keys):
    return {key: value for key, value in data.items() if key not in excluded_keys}


def clean_data(data):
    """
    Convert all datetime objects to str, for serialization (recursively).
    """
    if isinstance(data, datetime):
        return str(data)
    if isinstance(data, dict):
        return {key: clean_data(value) for key, value in data.items()}
    if isinstance(data, list):
        return [clean_data(d) for d in data]
    return data


def save_to(content, path):
    if path == "-":
        print(content)
        return
    with open(path, "w") as of:
        of.write(content)


if __name__ == "__main__":
    main()
