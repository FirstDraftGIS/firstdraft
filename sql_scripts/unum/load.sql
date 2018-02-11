/* takes about 7 minutes */

DROP TABLE IF EXISTS unum;

CREATE TABLE unum (
    admin1code varchar(100),
    admin2code varchar(101),
    admin3code varchar(102),
    admin4code varchar(103),
    admin_level smallint,
    asciiname varchar(2000),
    alternate_names varchar(100000),
    attribution varchar(1000),
    city varchar(1000),
    county varchar(1000),
    country varchar(1000),
    country_code varchar(2),
    dem varchar(1000),
    display_name varchar(12345),
    elevation varchar(105),
    east float,
    geoname_feature_class varchar(1000),
    geoname_feature_code varchar(1000),
    geonameid bigint,
    importance decimal,
    latitude float NOT NULL,
    longitude float NOT NULL,
    name varchar(2000) NOT NULL,
    name_en varchar(2000) NOT NULL,
    north float,
    osmname_class varchar(1000),
    osmname_type varchar(1000),
    osm_type varchar(106),
    osm_id varchar(107),
    place_rank int,
    place_type varchar(1),
    population bigint,
    south float,
    state varchar(1000),
    street varchar(1000),
    timezone varchar(40),
    west float,
    enwiki_title varchar(5023)
);

COPY unum FROM '/tmp/unum.tsv' WITH (FORMAT 'csv', DELIMITER E'\t', HEADER, NULL '');
