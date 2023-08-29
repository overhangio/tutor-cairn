DROP TABLE IF EXISTS _courseware_studentmodule;
CREATE TABLE _courseware_studentmodule
(
    `student_id` UInt64,
    `modified` DateTime NULL
)
ENGINE = MySQL('{{ MYSQL_HOST }}:{{ MYSQL_PORT }}', '{{ OPENEDX_MYSQL_DATABASE }}', 'courseware_studentmodule', '{{ OPENEDX_MYSQL_USERNAME }}', '{{ OPENEDX_MYSQL_PASSWORD }}');


DROP TABLE IF EXISTS openedx_user_last_course_activity;

set allow_experimental_live_view = 1;


CREATE LIVE VIEW openedx_user_last_course_activity WITH PERIODIC REFRESH 30 AS
SELECT
    _courseware_studentmodule.student_id AS user_id,
    max(_courseware_studentmodule.modified) AS last_course_activity
FROM _courseware_studentmodule
GROUP BY _courseware_studentmodule.student_id ;

DROP POLICY IF EXISTS common ON openedx_user_last_course_activity;
-- Grant everyone access to the view
CREATE ROW POLICY common ON openedx_user_last_course_activity FOR SELECT USING 1 TO ALL;