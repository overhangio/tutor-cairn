CREATE TABLE tracking
(
    `time` DateTime,
    `message` String,
) ENGINE MergeTree
ORDER BY time;

CREATE TABLE events
(
    `time` DateTime,
    `message` String,
    `name` String,
    `course_id` String,
    `user_id` Int64,
    `event_source` String
)
ENGINE MergeTree
ORDER BY time;

CREATE MATERIALIZED VIEW events_mv TO events AS
SELECT
    time,
    JSONExtractString(message, 'name') AS name,
    JSONExtract(message, 'context', 'course_id', 'String') AS course_id,
    JSONExtract(message, 'context', 'user_id', 'Int64') AS user_id,
    JSONExtractString(message, 'event_source') AS event_source
FROM tracking;

-- Grant everyone access to the view
CREATE ROW POLICY common ON events FOR SELECT USING 1 TO ALL;
