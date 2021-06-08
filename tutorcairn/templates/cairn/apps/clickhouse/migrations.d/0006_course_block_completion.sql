CREATE TABLE _openedx_block_completion
(
    `modified` DateTime NULL,
    `course_key` String,
    `block_key` String,
    `block_type` String,
    `user_id` UInt64,
    `completion` Float32
)
ENGINE = MySQL('{{ MYSQL_HOST }}:{{ MYSQL_PORT }}', '{{ OPENEDX_MYSQL_DATABASE }}', 'completion_blockcompletion', '{{ OPENEDX_MYSQL_USERNAME }}', '{{ OPENEDX_MYSQL_PASSWORD }}');

-- enable live views
set allow_experimental_live_view = 1;

CREATE LIVE VIEW course_block_completion WITH PERIODIC REFRESH 30 AS
SELECT
    _openedx_block_completion.course_key AS course_id,
    _openedx_block_completion.block_key AS block_key,
    _openedx_block_completion.user_id AS user_id,
    _openedx_block_completion.completion AS completion,
    course_blocks.position as position,
    course_blocks.display_name as display_name,
    course_blocks.full_name as full_name
FROM _openedx_block_completion
INNER JOIN course_blocks ON _openedx_block_completion.block_key = course_blocks.block_key;

-- Grant everyone access to the view
CREATE ROW POLICY common ON course_block_completion FOR SELECT USING 1 TO ALL;
