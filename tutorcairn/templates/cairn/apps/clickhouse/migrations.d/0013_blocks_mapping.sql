Drop TABLE IF EXISTS block_mapping;

set allow_experimental_live_view = 1;

CREATE LIVE VIEW block_mapping WITH PERIODIC REFRESH 30 AS 
SELECT 
    course_id,
    substring(full_name FROM 1 FOR (length(full_name) - position('>' IN reverse(full_name)))) AS parent_block, 
    Count(block_key) as total_blocks
FROM course_blocks
WHERE ROUND((LENGTH(full_name) - LENGTH(REPLACE(full_name, '>', '')))) = 4
group by course_id, parent_block;

DROP POLICY IF EXISTS common ON block_mapping;

CREATE ROW POLICY common ON block_mapping FOR SELECT USING 1 TO ALL;

