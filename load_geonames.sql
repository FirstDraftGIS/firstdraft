CREATE EXTENSION file_fdw;
CREATE SERVER geoname_server FOREIGN DATA WRAPPER file_fdw;
CREATE FOREIGN TABLE appfd_geoname (
            geonameid integer,
            name varchar(200),
            asciiname varchar(200),
            alternatenames varchar(10000),
            latitude decimal(8),
            longitude decimal(8),
            feature_class char(1),
            feature_code varchar(10),
            country_code varchar(2),
            cc2 varchar(200),
            admin1_code varchar(20),
            admin2_code varchar(80),
            admin3_code varchar(20),
            admin4_code varchar(20),
            population bigint,
            elevation integer,
            dem integer,
            timezone varchar(40),
            modification_date varchar(40)
        )
        SERVER geoname_server
        OPTIONS ( filename '/tmp/allCountries.txt', format 'text' );

INSERT INTO appfd_place (geonameid, name, point, population, country_code, admin1_code, admin2_code) SELECT geonameid, name, ST_SetSRID(ST_POINT(longitude, latitude), 4326), population, country_code, admin1_code, admin2_code FROM appfd_geoname;
