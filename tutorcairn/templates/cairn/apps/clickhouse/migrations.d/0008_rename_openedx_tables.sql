RENAME TABLE openedx_course_enrollments TO _openedx_course_enrollments;
RENAME TABLE openedx_user_profiles TO _openedx_user_profiles;
RENAME TABLE openedx_users TO _openedx_users;

-- enable live views
set allow_experimental_live_view = 1;

DROP TABLE course_enrollments;
CREATE LIVE VIEW course_enrollments WITH PERIODIC REFRESH 30 AS
SELECT
    _openedx_course_enrollments.course_id AS course_id,
    _openedx_course_enrollments.created AS enrollment_created,
    _openedx_course_enrollments.is_active AS enrollment_is_active,
    _openedx_course_enrollments.mode AS enrollment_mode,
    _openedx_course_enrollments.user_id AS user_id,
    _openedx_users.username AS username,
    _openedx_users.email AS user_email,
    _openedx_user_profiles.year_of_birth AS user_year_of_birth,
    _openedx_user_profiles.gender AS user_gender,
    _openedx_user_profiles.level_of_education AS user_level_of_education,
    _openedx_user_profiles.city AS user_city,
    _openedx_user_profiles.state AS user_state,
    _openedx_user_profiles.country AS user_country
FROM _openedx_course_enrollments
INNER JOIN _openedx_user_profiles ON _openedx_course_enrollments.user_id = _openedx_user_profiles.user_id
INNER JOIN _openedx_users ON _openedx_course_enrollments.user_id = _openedx_users.id;
