-- Here we add a 'end_position >= start_position' constraint, to avoid broken segments.
-- It happens, in particular when users pause/play/skip quickly.
CREATE OR REPLACE VIEW video_view_segments AS
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
WHERE end_event IN ('pause_video', 'stop_video', 'seek_video')
AND end_position >= start_position;
