DROP TABLE IF EXISTS openedx_course_overview;
CREATE TABLE openedx_course_overview
(
    `id` String,
    `display_name` String,
    `display_number_with_default` String,
    `display_org_with_default` String,
    `start` DateTime NULL,
    `end` DateTime NULL
)
ENGINE = MySQL('{{ MYSQL_HOST }}:{{ MYSQL_PORT }}', '{{ OPENEDX_MYSQL_DATABASE }}', 'course_overviews_courseoverview', '{{ OPENEDX_MYSQL_USERNAME }}', '{{ OPENEDX_MYSQL_PASSWORD }}');

DROP POLICY IF EXISTS common ON openedx_course_overview;

-- Grant everyone access
CREATE ROW POLICY common ON openedx_course_overview FOR SELECT USING 1 TO ALL;

DROP TABLE IF EXISTS _openedx_access_role;

CREATE TABLE _openedx_access_role
(
    `id` UInt64,
    `course_id` String,
    `role` String,
    `user_id` UInt64
)
ENGINE = MySQL('{{ MYSQL_HOST }}:{{ MYSQL_PORT }}', '{{ OPENEDX_MYSQL_DATABASE }}', 'student_courseaccessrole', '{{ OPENEDX_MYSQL_USERNAME }}', '{{ OPENEDX_MYSQL_PASSWORD }}');


DROP TABLE IF EXISTS openedx_course_detail;

set allow_experimental_live_view = 1;

CREATE LIVE VIEW openedx_course_detail WITH PERIODIC REFRESH 30 AS
SELECT
    openedx_course_overview.id AS course_id,
    openedx_course_overview.display_name AS course_name,
    openedx_course_overview.display_number_with_default AS course_number,
    openedx_course_overview.display_org_with_default AS org,
    openedx_course_overview.start AS start_date,
    openedx_course_overview.end AS end_date,
    openedx_user_info_detail.user_fullname AS instructor
FROM openedx_course_overview
INNER JOIN _openedx_access_role ON _openedx_access_role.course_id=openedx_course_overview.id
INNER JOIN openedx_user_info_detail ON openedx_user_info_detail.user_id = _openedx_access_role.user_id
where _openedx_access_role.role='instructor';


DROP POLICY IF EXISTS common ON openedx_course_detail;

-- Grant everyone access to the view
CREATE ROW POLICY common ON openedx_course_detail FOR SELECT USING 1 TO ALL;
