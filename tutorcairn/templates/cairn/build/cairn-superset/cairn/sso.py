import logging
import typing as t

from flask import session
from superset.security import SupersetSecurityManager

from . import bootstrap as cairn_bootstrap

logger = logging.getLogger(__name__)


OPENEDX_SSO_PROVIDER = "openedx"


class OpenEdxSsoSecurityManager(SupersetSecurityManager):
    def oauth_user_info(self, provider, response=None):
        """
        Identify the user
        """
        if provider == OPENEDX_SSO_PROVIDER:
            try:
                return self.get_user_info()
            except Exception as e:
                # Log exceptions, otherwise the stacktrace is swallowed by
                # flask_appbuilder.security.views.AuthOAuthView.oauth_authorized
                logger.exception(e)
                raise

    def get_user_info(self):
        """
        Make calls to the LMS API to fetch user information
        http://local.openedx.io:8000/api-docs/#/user/user_v1_me_read
        """
        username = self.get_lms_api("/api/user/v1/me")["username"]
        account = self.get_lms_api(f"/api/user/v1/accounts/{username}")

        # Fetch list of courses in which user is staff
        courses = [
            c["course_id"]
            for c in self.get_lms_api(
                f"/api/courses/v1/courses/?permissions=staff&username={username}"
            )["results"]
        ]
        if not courses:
            # User is not staff, entry is forbidden
            return {}

        # Create role, db, clickhouse db associated to user
        cairn_bootstrap.setup_user(username, course_ids=courses)

        # See flask_appbuilder.security.manager.BaseSecurityManager.auth_user_oauth for
        # valid keys
        return {
            "name": account["name"],
            "email": account["email"],
            "id": username,
            "username": username,
        }

    def get_lms_api(self, endpoint):
        """
        Make a call to the LMS API using the client app credentials.
        """
        return (
            self.appbuilder.sm.oauth_remotes[OPENEDX_SSO_PROVIDER].get(endpoint).json()
        )

    def _oauth_calculate_user_roles(self, userinfo) -> t.List[str]:
        """
        Override parent method to be able to create groups that match the user name.

        This is a bit hackish, but the cleanest solution we found.
        """
        roles = []
        for name in cairn_bootstrap.get_role_names(userinfo["username"]):
            role = self.find_role(name)
            if role:
                roles.append(role)
            else:
                logger.error("Could not find role: %s", name)

        # If user is already a member of one of these roles, preserve them.
        if user := self.find_user(username=userinfo["username"]):
            roles_to_preserve = ["Admin"]
            for role_to_preserve in roles_to_preserve:
                role = self.find_role(role_to_preserve)
                if role in user.roles:
                    roles.append(role)

        return roles

    def set_oauth_session(self, provider, oauth_response):
        """
        Store the oauth token in the session for later retrieval.
        """
        super().set_oauth_session(provider, oauth_response)

        if provider == OPENEDX_SSO_PROVIDER:
            session["oauth_token"] = oauth_response
