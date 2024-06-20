from functools import lru_cache
import json
import logging
import os

import requests
from superset.extensions import db, security_manager
from superset.utils.database import get_or_create_db

logger = logging.getLogger(__name__)

# sql_lab is required in 2.1.0 for non-admin users to get access to sql queries
DEFAULT_ROLES = ["Gamma", "sql_lab"]

def setup_user(username: str, course_ids=None) -> None:
    """
    Create clickhouse DB, superset role, and superset DB associated to user.
    This role will have access to the database with the same name.
    """
    clickhouse_username = f"openedx-{username}"
    superset_db = f"openedx-{username}"
    superset_role = get_user_role_name(username)

    create_clickhouse_user(clickhouse_username)
    grant_clickhouse_row_based_access(clickhouse_username, course_ids=course_ids)
    create_superset_db(superset_db, clickhouse_username)
    create_superset_db_role(superset_role, superset_db)

def get_role_names(username: str) -> str:
    """
    Return all the role names normally associated to a user.
    """
    return DEFAULT_ROLES + [get_user_role_name(username)]

def get_user_role_name(username: str) -> str:
    """
    Return the user-specific role name associated to a user.
    """
    return f"openedx-{username}"

def create_superset_db(superset_database: str, clickhouse_username: str) -> None:
    """
    Create a database object with the right Clickhouse URI:

    - user: clickhouse_username
    - password: None
    - host/port: clickhouse host/port
    - database: database name

    User will be able to access the Clickhouse DB without any password, but should only
    be granted access to the right rows.
    """
    # https://superset.apache.org/docs/databases/clickhouse
    auth = get_clickhouse_credentials()
    uri = f"clickhousedb://{clickhouse_username}:@{auth['host']}:{auth['http_port']}/{auth['database']}"
    logger.info("Creating Superset DB: %s", uri)
    superset_db = get_or_create_db(superset_database, uri, always_create=True)
    db.session.add(superset_db)
    db.session.commit()


def create_superset_db_role(role_name: str, superset_database_name: str) -> None:
    """
    Create a role that has basic access permissions for a certain database.
    """

    def check_permission(permission_view) -> bool:
        """
        The list of all available permissions can be obtained from the admin role:

            print(security_manager.find_role("Admin").permissions)
        """
        permission_name = str(permission_view)
        if permission_name in [
            "can save on Datasource",
            "can sql json on Superset",
            "menu access on Datasets",
            # Modify "see table schema" dropdown in sql lab
            "can expanded on TableSchemaView",
            "can delete on TableSchemaView",
            "can post on TableSchemaView",
        ]:
            return True
        if permission_name.startswith(f"database access on [{superset_database_name}]"):
            return True
        if permission_name.startswith(f"schema access on [{superset_database_name}]"):
            return True
        return False

    # Create or update role with the same name as the user
    pvms = security_manager._get_all_pvms()
    security_manager.set_role(role_name, check_permission, pvms)


def create_clickhouse_user(clickhouse_username):
    """
    Create a password-less clickhouse user with access to Clickhouse.
    """
    make_clickhouse_query(f"""CREATE USER IF NOT EXISTS '{clickhouse_username}';""")
    make_clickhouse_query(
        f"""GRANT CREATE TEMPORARY TABLE ON *.* TO '{clickhouse_username}';"""
    )


def grant_clickhouse_row_based_access(clickhouse_username, course_ids=None):
    """
    Grant row-based access to a Clickhouse user based on a selection of course IDs.

    When the list of course IDs is None, grant access to all courses.
    """
    if course_ids:
        condition = " OR ".join(
            [f"course_id = '{course_id}'" for course_id in course_ids]
        )
    else:
        condition = "1"
    # Find the list of tables to which the user should have access: all tables that do not start with "_"
    for table in make_clickhouse_query("SHOW TABLES").split("\n"):
        if not table.startswith("_"):
            make_clickhouse_query(
                        f"""GRANT SELECT ON {table} TO '{clickhouse_username}';"""
                    )
                    
            if table in ["openedx_users", "openedx_user_profiles", "openedx_block_completion"]:
                make_clickhouse_query(
                    f"""CREATE ROW POLICY OR REPLACE '{clickhouse_username}' ON {table} AS RESTRICTIVE FOR SELECT USING 1 TO '{clickhouse_username}';"""
                )
            else:
                make_clickhouse_query(
                    f"""CREATE ROW POLICY OR REPLACE '{clickhouse_username}' ON {table} AS RESTRICTIVE FOR SELECT USING {condition} TO '{clickhouse_username}';"""
                )


def make_clickhouse_query(query):
    """
    Query Clickhouse by POSTing some content by http.
    """
    logger.info("Running Clickhouse query: %s", query)
    auth = get_clickhouse_credentials()
    clickhouse_uri = f"{auth['http_scheme']}://{auth['username']}:{auth['password']}@{auth['host']}:{auth['http_port']}/?database={auth['database']}"
    response = requests.post(clickhouse_uri, data=query.encode("utf8"), timeout=10)
    if response.status_code != 200:
        raise ValueError(
            f"An error occurred while attempting to post a query: {response.content.decode()}"
        )
    return response.content.decode("utf8").strip()


@lru_cache(maxsize=None)
def get_clickhouse_credentials():
    """
    Load the clickhouse credentials from file.
    """
    with open(
        os.path.join(os.path.dirname(__file__), "clickhouse-auth.json"),
        encoding="utf-8",
    ) as f:
        return json.load(f)
