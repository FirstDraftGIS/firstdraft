CREATE OR REPLACE FUNCTION conflate(target varchar, lat double precision, lon double precision, cc varchar DEFAULT NULL, pop int DEFAULT NULL)
RETURNS void AS $$
    WITH updated AS (
        UPDATE appfd_place SET
            population = (CASE WHEN population IS NULL and pop IS NOT NULL THEN pop ELSE population END),
            country_code = (CASE WHEN country_code IS NULL and cc IS NOT NULL THEN cc ELSE country_code END)
        WHERE id = (
            WITH data AS (
                SELECT
                    *,
                    ST_DWithin(CAST(ST_SetSRID(ST_Point(lon, lat), 4326) As geography), point, 1) AS d1,
                    ST_DWithin(CAST(ST_SetSRID(ST_Point(lon, lat), 4326) As geography), point, 10) AS d10,
                    ST_DWithin(CAST(ST_SetSRID(ST_Point(lon, lat), 4326) As geography), point, 100) AS d100,
                    ST_DWithin(CAST(ST_SetSRID(ST_Point(lon, lat), 4326) As geography), point, 1000) AS d1000,
                    ST_DWithin(CAST(ST_SetSRID(ST_Point(lon, lat), 4326) As geography), point, 10000) AS d10000,
                    pop IS NOT NULL AS pop_exists,
                    CASE WHEN pop IS NOT NULL AND population > 0 THEN abs(pop - population)::decimal / GREATEST(pop, population)::decimal < 0.05 ELSE false END AS pop_is_close,
                    admin_level IS NOT NULL AS has_admin_level
                FROM appfd_place WHERE name = target
            )
            SELECT id
            AS score
            FROM data
            WHERE d1 IS true OR d10 is true or d100 is true or d1000 is true or d10000 is true
            ORDER BY
                d1::int * 10000 +
                d10::int * 1000 +
                d100::int * 100 +
                d1000::int * 10 +
                d10000::int * 1 +
                pop_exists::int * 10 +
                pop_is_close::int * 1000
            DESC
        LIMIT 1)
    RETURNING *
    )
    INSERT INTO appfd_place
        (country_code, name, point, population)
        SELECT cc, target, ST_SetSRID(ST_Point(lon, lat), 4326), pop
        WHERE NOT EXISTS (SELECT * FROM updated);
$$ LANGUAGE sql VOLATILE;
