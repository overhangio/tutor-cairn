CREATE TABLE course_blocks
(
    `course_id` String,
    `block_key` String,
    `block_id` String,
    `position` Integer,
    `display_name` String,
    `full_name` String
)
ENGINE MergeTree
ORDER BY (course_id, position, block_id);

-- Grant everyone access to the table
CREATE ROW POLICY common ON course_blocks FOR SELECT USING 1 TO ALL;
