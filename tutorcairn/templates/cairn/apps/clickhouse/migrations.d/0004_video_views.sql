CREATE TABLE video_events
(
    `course_id` String,
    `video_id` String,
    `user_id` Int64,
    `name` String,
    `time` DateTime,
    `position` Float
)
ENGINE MergeTree
ORDER BY time;

-- Collect video events and store them in the video_events table
CREATE MATERIALIZED VIEW _video_events_mv TO video_events AS
SELECT
    JSONExtract(message, 'context', 'course_id', 'String') AS course_id,
    JSONExtractString(JSONExtractString(message, 'event'), 'id') as video_id,
    JSONExtract(message, 'context', 'user_id', 'Int64') AS user_id,
    JSONExtractString(message, 'name') as name,
    time,
    JSONExtractFloat(JSONExtractString(message, 'event'), 'currentTime') AS position
FROM _tracking
WHERE name IN ('play_video', 'pause_video', 'stop_video');
CREATE MATERIALIZED VIEW _video_seek_events_mv TO video_events AS
SELECT
    JSONExtract(message, 'context', 'course_id', 'String') AS course_id,
    JSONExtractString(JSONExtractString(message, 'event'), 'id') as video_id,
    JSONExtract(message, 'context', 'user_id', 'Int64') AS user_id,
    JSONExtractString(message, 'name') as name,
    time,
    JSONExtractFloat(JSONExtractString(message, 'event'), 'old_time') AS position
FROM _tracking
WHERE name = 'seek_video';

-- For ease of access, create a simple view to aggregate the viewed video segments
CREATE VIEW video_view_segments AS
SELECT
    course_id,
    video_id,
    user_id,
    start_time,
    start_position,
    start_event,
    time as end_time,
    position AS end_position,
    name as end_event,
    end_position - start_position as duration
FROM video_events AS video_events_end
ASOF LEFT JOIN (
    SELECT
        time as start_time,
        course_id AS course_id_start,
        video_id as video_id_start,
        user_id AS user_id_start,
        name as start_event,
        position AS start_position
    FROM video_events
    WHERE start_event = 'play_video'
) AS video_events_start
ON course_id_start = course_id AND video_id_start = video_id AND user_id_start = user_id AND start_time < end_time
WHERE end_event IN ('pause_video', 'stop_video', 'seek_video');


CREATE ROW POLICY common ON video_events FOR SELECT USING 1 TO ALL;
CREATE ROW POLICY common ON video_view_segments FOR SELECT USING 1 TO ALL;
