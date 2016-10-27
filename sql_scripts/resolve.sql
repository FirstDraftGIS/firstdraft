CREATE INDEX index_name_first_char ON appfd_place (LEFT(name,1));
CREATE INDEX index_name_char_length ON appfd_place (char_length(name));
CREATE INDEX idx_places_trgm_gist_name ON appfd_place USING gist (name gist_trgm_ops);
CREATE INDEX idx_places_trgm_gin_name ON appfd_place USING gin (name gin_trgm_ops);
set_limit(0.5);

CREATE FUNCTION indexOf(haystack ANYARRAY, needle ANYELEMENT)
RETURNS INT AS $$
    SELECT i
      FROM generate_subscripts(haystack, 1) AS i
     WHERE haystack[i] = needle
  ORDER BY i
$$ LANGUAGE sql STABLE;

CREATE OR REPLACE FUNCTION calc_popularity(placeid int)
RETURNS int AS $$
    SELECT count(appfd_featureplace.id)::int FROM appfd_featureplace INNER JOIN appfd_feature ON (appfd_featureplace.feature_id = appfd_feature.id) WHERE appfd_feature.verified = true AND appfd_featureplace.correct = true AND appfd_featureplace.place_id = placeid;
$$ LANGUAGE sql STABLE;

DROP TYPE geoentity CASCADE;
create type geoentity as (
  place_id int,
  admin_level int,
  country_code varchar,
  admin1_code varchar,
  ccrank int,
  target text,
  place_name varchar,
  alias varchar,
  population bigint,
  point geometry(Point,4326),
  topic_id int,
  has_mpoly boolean,
  has_pcode boolean,
  popularity int
);

DROP FUNCTION fdgis_resolve(text[], thorough boolean DEFAULT false);
CREATE OR REPLACE FUNCTION
fdgis_resolve(names text[], thorough boolean DEFAULT false)
RETURNS setof geoentity AS $$
DECLARE
    geoentities geoentity%rowtype;
    firstchars text[];
    country_code_rankings varchar[];
    most_common_country_code varchar;
BEGIN
    country_code_rankings := ARRAY(SELECT country_code from appfd_place WHERE name = ANY(names) GROUP BY 1 ORDER BY count(1) DESC);
    RETURN QUERY SELECT id, admin_level, country_code, admin1_code, indexOf(country_code_rankings, country_code), name || '--0', name, NULL::varchar, population, point, topic_id, mpoly IS NOT NULL, pcode IS NOT NULL, calc_popularity(id) as subquery1 FROM appfd_place WHERE name = ANY(names) AND point IS NOT NULL;
    RETURN QUERY SELECT appfd_place.id, appfd_place.admin_level, country_code, admin1_code, indexOf(country_code_rankings, country_code), appfd_alias.alias || '--0', appfd_place.name, appfd_alias.alias, appfd_place.population, appfd_place.point, appfd_place.topic_id, appfd_place.mpoly IS NOT NULL, appfd_place.pcode IS NOT NULL, calc_popularity(appfd_place.id) as subquery2 FROM appfd_place INNER JOIN appfd_aliasplace on (appfd_place.id = appfd_aliasplace.place_id) INNER JOIN appfd_alias ON (appfd_aliasplace.alias_id = appfd_alias.id) WHERE appfd_place.point IS NOT NULL AND appfd_alias.alias = ANY(names);
    most_common_country_code := country_code_rankings[0];
    firstchars := (SELECT ARRAY(SELECT left(name, 1) FROM unnest(names) AS name));
    IF thorough THEN
        RETURN QUERY
            SELECT id, admin_level, country_code, admin1_code, indexOf(country_code_rankings, country_code), (SELECT target || '--' || ldist FROM (SELECT target, levenshtein_less_equal(target, appfd_place.name, 2) AS ldist FROM unnest(names::TEXT[]) AS target ORDER BY ldist LIMIT 1) as s1)::text, name, NULL::varchar, population, point, topic_id, mpoly IS NOT NULL, pcode IS NOT NULL, calc_popularity(id)
            FROM appfd_place
            WHERE country_code = most_common_country_code
            AND appfd_place.point IS NOT NULL
            AND left(name, 1) = ANY(firstchars)
            AND name != ANY(names)
            AND TRUE IN (SELECT levenshtein_less_equal(n, name, 2) <= 2 FROM unnest(names) AS n);
    END IF;
    RETURN;
END; $$
LANGUAGE PLPGSQL;

DROP FUNCTION fdgis_resolve_with_countries(names text[], countries text[], thorough boolean DEFAULT false);
CREATE OR REPLACE FUNCTION
fdgis_resolve_with_countries(names text[], countries text[], thorough boolean DEFAULT false)
RETURNS setof geoentity AS $$
DECLARE
    geoentities geoentity%rowtype;
    firstchars text[];
    country_code_rankings varchar[];
    most_common_country_code varchar;
    country_codes varchar[];
BEGIN
    country_codes := ARRAY(SELECT country_code FROM appfd_place WHERE admin_level = 0 AND name = ANY(countries));
    country_code_rankings := ARRAY(SELECT country_code from appfd_place WHERE name = ANY(names) GROUP BY 1 ORDER BY count(1) DESC);
    RETURN QUERY SELECT id, admin_level, country_code, admin1_code, indexOf(country_code_rankings, country_code), name || '--0', name, NULL::varchar, population, point, topic_id, mpoly IS NOT NULL, pcode IS NOT NULL, calc_popularity(id) as subquery1 FROM appfd_place WHERE country_code = ANY(country_codes) AND name = ANY(names) AND point IS NOT NULL;
    RETURN QUERY SELECT appfd_place.id, appfd_place.admin_level, country_code, admin1_code, indexOf(country_code_rankings, country_code), appfd_alias.alias || '--0', appfd_place.name, appfd_alias.alias, appfd_place.population, appfd_place.point, appfd_place.topic_id, appfd_place.mpoly IS NOT NULL, appfd_place.pcode IS NOT NULL, calc_popularity(appfd_place.id) as subquery2 FROM appfd_place INNER JOIN appfd_aliasplace on (appfd_place.id = appfd_aliasplace.place_id) INNER JOIN appfd_alias ON (appfd_aliasplace.alias_id = appfd_alias.id) WHERE appfd_place.country_code = ANY(country_codes) AND appfd_place.point IS NOT NULL AND appfd_alias.alias = ANY(names);
    most_common_country_code := country_code_rankings[0];
    firstchars := (SELECT ARRAY(SELECT left(name, 1) FROM unnest(names) AS name));
    IF thorough THEN
        RETURN QUERY
            SELECT id, admin_level, country_code, admin1_code, indexOf(country_code_rankings, country_code), (SELECT target || '--' || ldist FROM (SELECT target, levenshtein_less_equal(target, appfd_place.name, 2) AS ldist FROM unnest(names::TEXT[]) AS target ORDER BY ldist LIMIT 1) as s1)::text, name, NULL::varchar, population, point, topic_id, mpoly IS NOT NULL, pcode IS NOT NULL, calc_popularity(id)
            FROM appfd_place
            WHERE country_code = most_common_country_code
            AND appfd_place.point IS NOT NULL
            AND left(name, 1) = ANY(firstchars)
            AND name != ANY(names)
            AND TRUE IN (SELECT levenshtein_less_equal(n, name, 2) <= 2 FROM unnest(names) AS n);
    END IF;
    RETURN;
END; $$
LANGUAGE PLPGSQL;







SELECT target FROM fdgis_resolve('{Afghanistan, Kuwaiti, Italy}'::TEXT[]);
