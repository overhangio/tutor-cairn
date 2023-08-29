Drop TABLE IF EXISTS openedx_users_info;

CREATE TABLE openedx_users_info
(
    `id` UInt64,
    `username` String,
    `email` String,
    `is_staff` UInt8,
    `is_superuser` UInt8,
    `is_active` UInt8,
    `last_login` DateTime NULL,
    `date_joined` DateTime
)
ENGINE = MySQL('{{ MYSQL_HOST }}:{{ MYSQL_PORT }}', '{{ OPENEDX_MYSQL_DATABASE }}', 'auth_user', '{{ OPENEDX_MYSQL_USERNAME }}', '{{ OPENEDX_MYSQL_PASSWORD }}');


DROP POLICY IF EXISTS common ON openedx_users_info;

-- Grant everyone access
CREATE ROW POLICY common ON openedx_users_info FOR SELECT USING 1 TO ALL;