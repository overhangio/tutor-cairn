CREATE TABLE course_grades
(
    `percent_grade` Double,
    `passed_timestamp` DateTime NULL,
    `user_id` UInt64,
    `course_id` String
)
ENGINE = MySQL('{{ MYSQL_HOST }}:{{ MYSQL_PORT }}', '{{ OPENEDX_MYSQL_DATABASE }}', 'grades_persistentcoursegrade', '{{ OPENEDX_MYSQL_USERNAME }}', '{{ OPENEDX_MYSQL_PASSWORD }}');

-- Grant everyone access to the view
CREATE ROW POLICY common ON course_grades FOR SELECT USING 1 TO ALL;
