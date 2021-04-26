CREATE TABLE openedx_courseenrollments
(
    `created` DateTime NULL,
    `user_id` UInt64,
    `course_id` String,
    `is_active` UInt8,
    `mode` String
)
ENGINE = MySQL('{{ MYSQL_HOST }}:{{ MYSQL_PORT }}', '{{ OPENEDX_MYSQL_DATABASE }}', 'student_courseenrollment', '{{ OPENEDX_MYSQL_USERNAME }}', '{{ OPENEDX_MYSQL_PASSWORD }}');

CREATE TABLE openedx_userprofiles
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

-- enable live views
set allow_experimental_live_view = 1;

CREATE LIVE VIEW courseenrollments WITH PERIODIC REFRESH 30 AS
SELECT
    openedx_courseenrollments.course_id AS course_id,
    openedx_courseenrollments.created AS enrollment_created,
    openedx_courseenrollments.is_active AS enrollment_is_active,
    openedx_courseenrollments.mode AS enrollment_mode,
    openedx_courseenrollments.user_id AS user_id,
    openedx_userprofiles.year_of_birth AS user_year_of_birth,
    openedx_userprofiles.gender AS user_gender,
    openedx_userprofiles.level_of_education AS user_level_of_education,
    openedx_userprofiles.city AS user_city,
    openedx_userprofiles.state AS user_state,
    openedx_userprofiles.country AS user_country
FROM openedx_courseenrollments
INNER JOIN openedx_userprofiles ON openedx_courseenrollments.user_id = openedx_userprofiles.user_id;

-- Grant everyone access to the view
CREATE ROW POLICY common ON courseenrollments FOR SELECT USING 1 TO ALL;
