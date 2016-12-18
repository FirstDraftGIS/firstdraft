CREATE EXTENSION IF NOT EXISTS file_fdw;


DROP FOREIGN TABLE IF EXISTS alternateNames CASCADE;
DROP SERVER IF EXISTS alternateNames;

CREATE SERVER alternateNames FOREIGN DATA WRAPPER file_fdw;

CREATE FOREIGN TABLE alternateNames (
    geonameid integer,
    a integer,
    language text,
    alternate_name text,
    b text,
    c text,
    d text,
    e text

) SERVER alternateNames
OPTIONS ( filename '/tmp/alternateNames.txt', format 'csv', delimiter E'\t',quote E'\b');


CREATE OR REPLACE FUNCTION 

loadAlternateName(name text, lang text, gid integer)
    
RETURNS void AS $$

    DECLARE
        aliasid int;
        placeid int;
        aliasplaceid int;

    BEGIN

    aliasid := (SELECT id FROM appfd_alias WHERE alias = name LIMIT 1);
    IF aliasid IS NULL THEN
        INSERT INTO appfd_alias (alias, language) VALUES (name, lang) RETURNING id INTO aliasid;
    END IF;

    placeid := (SELECT id FROM appfd_place WHERE geonameid = gid);

    IF placeid IS NOT NULL THEN

        aliasplaceid := (SELECT id FROM appfd_aliasplace WHERE alias_id = aliasid AND place_id = placeid);
        if aliasplaceid IS NULL THEN
            INSERT INTO appfd_aliasplace (alias_id, place_id) VALUES (aliasid, placeid);
        END IF;

    END IF;

END; $$
LANGUAGE PLPGSQL;

DO $$DECLARE r record;
BEGIN
    FOR r in SELECT * FROM alternateNames
    LOOP
        EXECUTE loadAlternateName(r.alternate_name, r.language, r.geonameid);
    END LOOP;
END$$;


