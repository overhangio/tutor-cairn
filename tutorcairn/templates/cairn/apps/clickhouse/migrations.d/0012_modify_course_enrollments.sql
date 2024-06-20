RENAME TABLE _openedx_course_enrollments TO openedx_course_enrollments;
RENAME TABLE _openedx_user_profiles TO openedx_user_profiles;
RENAME TABLE _openedx_users TO openedx_users;

DROP TABLE course_enrollments;
CREATE VIEW course_enrollments AS
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
