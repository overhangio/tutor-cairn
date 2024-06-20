RENAME TABLE _openedx_block_completion TO openedx_block_completion;

DROP TABLE course_block_completion;

CREATE VIEW course_block_completion AS
SELECT
    openedx_block_completion.course_key AS course_id,
    openedx_block_completion.block_key AS block_key,
    openedx_block_completion.user_id AS user_id,
    openedx_block_completion.completion AS completion,
    course_blocks.position as position,
    course_blocks.display_name as display_name,
    course_blocks.full_name as full_name
FROM openedx_block_completion
INNER JOIN course_blocks ON openedx_block_completion.block_key = course_blocks.block_key;
