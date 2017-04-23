CREATE OR REPLACE FUNCTION  
update_country_codes()
RETURNS void AS $$
DECLARE  
    cc varchar;
    borders geometry(MultiPolygon,4326);
BEGIN
    FOR cc, borders IN
        SELECT country_code AS cc, mpoly AS borders
        FROM appfd_place
        WHERE admin_level = 0
    LOOP
        UPDATE appfd_place SET country_code = cc WHERE country_code IS NULL and st_contains(borders, point);
    END LOOP;
END; $$ 
LANGUAGE PLPGSQL;
