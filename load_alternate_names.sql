DROP FOREIGN TABLE IF EXISTS appfd_alternate_name;
CREATE FOREIGN TABLE IF NOT EXISTS appfd_alternate_name (
    alternateNameId integer,
    geonameid integer,
    isolanguage varchar(7),
    alternate_name varchar(200),
    isPreferredName integer,
    isShortName integer,
    isColloquial integer,
    isHistoric integer
    )
    SERVER geoname_server
    OPTIONS ( filename '/tmp/alternateNames.txt', format 'text' );

TRUNCATE appfd_alias CASCADE;


WITH x as (
    INSERT INTO appfd_alias (alias, entered, language)
    SELECT alternate_name, default, isolanguage
    FROM appfd_alternate_name
    LIMIT 5
    RETURNING id, SELECT place_id FROM appfd_place WHERE geonameid = geonameid
    )
INSERT INTO appfd_alias_place (alias_id, place_id) 
SELECT alias_id, place_id
FROM x;


WITH x AS (
    INSERT INTO bar (col1, col2)
    SELECT f.col1, f.col2
    FROM   foo f
    WHERE  f.id BETWEEN 12 AND 23 -- some filter
    RETURNING col1, col2, bar_id  -- assuming bar_id is a serial column
    )

INSERT INTO appfd_alias (geonameid, name, point, population, country_code, admin1_code, admin2_code) SELECT geonameid, name, ST_SetSRID(ST_POINT(longitude, latitude), 4326), population, country_code, admin1_code, admin2_code FROM appfd_geoname;


-- indexes database for faster searching
-- commenting out for now, because even with indexing, full text searching is slow
--ALTER TABLE appfd_place ADD COLUMN textsearchable_index_col tsvector;
--UPDATE appfd_place SET textsearchable_index_col =
--     to_tsvector('english', name);
--CREATE INDEX textsearch_idx ON appfd_place USING gin(textsearchable_index_col);

-- this should only take about 5 minutes
DROP INDEX IF EXISTS name_index;
CREATE INDEX name_index ON appfd_place (name);

