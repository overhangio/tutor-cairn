Drop TABLE IF EXISTS parent_child_block_mapping;

Drop TABLE IF EXISTS blockwise_course_progress;

-- enable live views
set allow_experimental_live_view = 1;

CREATE LIVE VIEW parent_child_block_mapping WITH PERIODIC REFRESH 30 AS
SELECT
    course_id,
    substring(full_name FROM 1 FOR (length(full_name) - position('>' IN reverse(full_name)))) AS parent_block, 
    block_key
FROM course_blocks;

DROP POLICY IF EXISTS common ON parent_child_block_mapping;

-- Grant everyone access to the view
CREATE ROW POLICY common ON parent_child_block_mapping FOR SELECT USING 1 TO ALL;


set allow_experimental_live_view = 1;

CREATE LIVE VIEW blockwise_course_progress WITH PERIODIC REFRESH 30 AS 
SELECT 
    _openedx_block_completion.course_key as course_id,
    pcbm.parent_block AS parent_block, 
    user_id,
    Sum(completion) as block_completed
FROM _openedx_block_completion
INNER JOIN parent_child_block_mapping as pcbm on pcbm.course_id=_openedx_block_completion.course_key and pcbm.block_key=_openedx_block_completion.block_key
group by course_id, parent_block, user_id;

DROP POLICY IF EXISTS common ON blockwise_course_progress;

CREATE ROW POLICY common ON blockwise_course_progress FOR SELECT USING 1 TO ALL;
