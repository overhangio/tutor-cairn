CREATE TABLE openedx_course_enrollments
(
    `created` DateTime NULL,
    `user_id` UInt64,
    `course_id` String,
    `is_active` UInt8,
    `mode` String
)
ENGINE = MySQL('{{ MYSQL_HOST }}:{{ MYSQL_PORT }}', '{{ OPENEDX_MYSQL_DATABASE }}', 'student_courseenrollment', '{{ OPENEDX_MYSQL_USERNAME }}', '{{ OPENEDX_MYSQL_PASSWORD }}');

CREATE TABLE openedx_user_profiles
(
    `user_id` UInt64,
    `year_of_birth` UInt32,
    `gender` String,
    `level_of_education` String,
    `city` String,
    `state` String,
    `country` String
)
ENGINE = MySQL('{{ MYSQL_HOST }}:{{ MYSQL_PORT }}', '{{ OPENEDX_MYSQL_DATABASE }}', 'auth_userprofile', '{{ OPENEDX_MYSQL_USERNAME }}', '{{ OPENEDX_MYSQL_PASSWORD }}');

CREATE TABLE openedx_users
(
    `id` UInt64,
    `username` String,
    `email` String
)
ENGINE = MySQL('{{ MYSQL_HOST }}:{{ MYSQL_PORT }}', '{{ OPENEDX_MYSQL_DATABASE }}', 'auth_user', '{{ OPENEDX_MYSQL_USERNAME }}', '{{ OPENEDX_MYSQL_PASSWORD }}');

-- enable live views
set allow_experimental_live_view = 1;

CREATE LIVE VIEW course_enrollments WITH PERIODIC REFRESH 30 AS
SELECT
    openedx_course_enrollments.course_id AS course_id,
    openedx_course_enrollments.created AS enrollment_created,
    openedx_course_enrollments.is_active AS enrollment_is_active,
    openedx_course_enrollments.mode AS enrollment_mode,
    openedx_course_enrollments.user_id AS user_id,
    openedx_users.username AS username,
    openedx_users.email AS user_email,
    openedx_user_profiles.year_of_birth AS user_year_of_birth,
    openedx_user_profiles.gender AS user_gender,
    openedx_user_profiles.level_of_education AS user_level_of_education,
    openedx_user_profiles.city AS user_city,
    openedx_user_profiles.state AS user_state,
    openedx_user_profiles.country AS user_country
FROM openedx_course_enrollments
INNER JOIN openedx_user_profiles ON openedx_course_enrollments.user_id = openedx_user_profiles.user_id
INNER JOIN openedx_users ON openedx_course_enrollments.user_id = openedx_users.id;

-- Grant everyone access to the view
CREATE ROW POLICY common ON course_enrollments FOR SELECT USING 1 TO ALL;
