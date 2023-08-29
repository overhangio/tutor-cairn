Drop TABLE IF EXISTS _auth_user_profiles;
DROP TABLE IF EXISTS openedx_user_info_detail;

CREATE TABLE _auth_user_profiles
(
    `user_id` UInt64,
    `year_of_birth` UInt32,
    `gender` String,
    `level_of_education` String,
    `city` String,
    `state` String,
    `country` String,
    `name` String
)
ENGINE = MySQL('{{ MYSQL_HOST }}:{{ MYSQL_PORT }}', '{{ OPENEDX_MYSQL_DATABASE }}', 'auth_userprofile', '{{ OPENEDX_MYSQL_USERNAME }}', '{{ OPENEDX_MYSQL_PASSWORD }}');


set allow_experimental_live_view = 1;


CREATE LIVE VIEW openedx_user_info_detail WITH PERIODIC REFRESH 30 AS
SELECT
    openedx_users_info.id AS user_id,
    openedx_users_info.username AS username,
    openedx_users_info.email AS user_email,
    openedx_users_info.is_staff AS is_staff,
    openedx_users_info.is_superuser AS is_superuser,
    openedx_users_info.is_active AS is_active,
    openedx_users_info.last_login as last_login,
    openedx_users_info.date_joined as date_joined,
    _auth_user_profiles.year_of_birth AS user_year_of_birth,
    _auth_user_profiles.gender AS user_gender,
    _auth_user_profiles.level_of_education AS user_level_of_education,
    _auth_user_profiles.city AS user_city,
    _auth_user_profiles.state AS user_state,
    _auth_user_profiles.country AS user_country,
    _auth_user_profiles.name AS user_fullname
FROM openedx_users_info
INNER JOIN _auth_user_profiles ON _auth_user_profiles.user_id=openedx_users_info.id;


DROP POLICY IF EXISTS common ON openedx_user_info_detail;

-- Grant everyone access to the view
CREATE ROW POLICY common ON openedx_user_info_detail FOR SELECT USING 1 TO ALL;