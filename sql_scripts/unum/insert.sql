INSERT INTO appfd_place
(
    attribution,
    enwiki_title, geonames_id, osm_id, pcode, fips,
    admin1_code, admin2_code, admin3_code, admin4_code, admin_level, /* admin stuff */
    east, north, south, west, /* bounding box */
    name, name_ascii, name_display, name_en, name_normalized, other_names,  /* name stuff */
    geonames_feature_class, geonames_feature_code, place_type, /* place types */
    latitude, longitude, mls, mpoly, point, area_sqkm, /* geometries */
    importance, osmname_class, osmname_type, place_rank, /* osm and osmnames stuff */
    dem, elevation, /* elevation stuff */
    city, county, country, country_code, state, street, /* geocoder stuff */
    note, population, popularity, timezone, topic_id
)
SELECT
    attribution,
    enwiki_title, geonameid, osm_id, NULL, NULL,
    admin1code, admin2code, admin3code, admin4code, admin_level,
    east, north, south, west,
    name, asciiname, display_name, name_en, lower(unaccent(asciiname)), alternate_names,
    geoname_feature_class, geoname_feature_code, place_type,
    latitude, longitude, NULL, NULL, ST_SetSRID(ST_Point(longitude, latitude), 4326), NULL,
    importance, osmname_class, osmname_type, place_rank,
    to_float(dem), to_float(elevation),
    city, county, country, country_code, state, street,
    NULL, population, 0, timezone, NULL
FROM unum
LIMIT 1000000000000;
