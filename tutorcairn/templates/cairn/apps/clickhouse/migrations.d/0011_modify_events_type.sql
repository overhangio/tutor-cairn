ALTER TABLE events 
MODIFY COLUMN user_id UInt64;

ALTER TABLE video_events 
MODIFY COLUMN user_id UInt64;
