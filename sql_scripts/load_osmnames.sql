CREATE OR REPLACE FUNCTION find_place_for_osm_name(target varchar, lat double precision, lon double precision, cc varchar)
RETURNS integer AS $$
    WITH data AS (
        SELECT
            *,
            ST_DWithin(CAST(ST_SetSRID(ST_Point(lon, lat), 4326) As geography), point, 1) AS d1,
            ST_DWithin(CAST(ST_SetSRID(ST_Point(lon, lat), 4326) As geography), point, 10) AS d10,
            ST_DWithin(CAST(ST_SetSRID(ST_Point(lon, lat), 4326) As geography), point, 100) AS d100,
            ST_DWithin(CAST(ST_SetSRID(ST_Point(lon, lat), 4326) As geography), point, 1000) AS d1000,
            ST_DWithin(CAST(ST_SetSRID(ST_Point(lon, lat), 4326) As geography), point, 10000) AS d10000,
            population IS NOT NULL AS pop_exists,
            admin_level IS NOT NULL AS has_admin_level
        FROM appfd_place WHERE name = target
    )
    SELECT id
    FROM data
    WHERE d1 IS true OR d10 is true or d100 is true or d1000 is true or d10000 is true
    ORDER BY
        d1::int * 10000 +
        d10::int * 1000 +
        d100::int * 100 +
        d1000::int * 10 +
        d10000::int * 1 +
        pop_exists::int * 10 +
        has_admin_level::int * 10
    DESC
    LIMIT 1

$$ LANGUAGE sql VOLATILE;



CREATE EXTENSION file_fdw;
CREATE SERVER osmnames FOREIGN DATA WRAPPER file_fdw;
DROP FOREIGN TABLE planet_latest;
CREATE FOREIGN TABLE planet_latest (
    name varchar NULL,
    alternative_names varchar NULL,
    osm_type varchar NULL,
    osm_id bigint NULL,
    class varchar NULL,
    _type varchar NULL,
    lon double precision NULL,
    lat double precision NULL,
    place_rank integer NULL,
    importance double precision NULL,
    street varchar NULL,
    city varchar NULL,
    county varchar NULL,
    state varchar NULL,
    country varchar NULL,
    country_code varchar NULL,
    display_name varchar NULL,
    west double precision NULL,
    south double precision NULL,
    east double precision NULL,
    north double precision NULL,
    wikidata varchar NULL DEFAULT NULL,
    wikipedia varchar NULL DEFAULT NULL
) SERVER osmnames
OPTIONS ( delimiter E'\t', filename '/tmp/planet-latest-cleaned.tsv', format 'csv', null 'NULL', quote '"');



CREATE OR REPLACE FUNCTION
load_osm_name(target varchar, lat double precision, lon double precision, cc varchar, new_importance double precision)
RETURNS void AS $$
DECLARE
    conflated_place_id int;
BEGIN

    /* Get Place if it already Exists */

    conflated_place_id := find_place_for_osm_name(target, lat, lon, cc);
    IF conflated_place_id IS NULL THEN
        INSERT INTO appfd_place (country_code, name, point) SELECT cc, target, ST_SetSRID(ST_Point(lon, lat), 4326) RETURNING id INTO conflated_place_id;
    END IF;
    
    UPDATE appfd_wikipedia SET importance = new_importance WHERE place_id = conflated_place_id;

    IF FOUND IS FALSE THEN
        INSERT INTO appfd_wikipedia (place_id, importance) SELECT conflated_place_id, new_importance;
    END IF;
    
END; $$
LANGUAGE PLPGSQL;
