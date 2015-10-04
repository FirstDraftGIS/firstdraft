

CREATE OR REPLACE VIEW v AS 
SELECT appfd_alternatename.alternate_name as name, appfd_alternatename.isolanguage as language, appfd_place.id as place_id FROM
appfd_place FULL OUTER JOIN appfd_alternatename ON appfd_place.geonameid = appfd_alternatename.geonameid;


TRUNCATE appfd_alias CASCADE;
TRUNCATE appfd_aliasplace CASCADE;

ALTER TABLE appfd_alias ADD COLUMN place_id integer;

WITH x AS (
    INSERT INTO appfd_alias (alias, language, place_id) SELECT name, language, place_id FROM v
    RETURNING id, place_id
)
INSERT INTO appfd_aliasplace (alias_id, place_id) SELECT id, place_id FROM x;

ALTER TABLE appfd_alias DROP COLUMN place_id;
DROP VIEW v;



