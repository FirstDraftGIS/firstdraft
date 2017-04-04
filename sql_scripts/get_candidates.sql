DROP FUNCTION get_candidates(text, text, thorough boolean);
CREATE OR REPLACE FUNCTION
get_candidates(target text, token text, thorough boolean DEFAULT false)
RETURNS setof geoentity AS $$
DECLARE
    geoentities geoentity%rowtype;
    most_common_country_code varchar;
BEGIN
    RETURN QUERY SELECT id, admin_level, appfd_place.country_code, admin1_code, (SELECT rank FROM appfd_countrycoderank WHERE order_id = token AND country_code = appfd_place.country_code LIMIT 1), name || '--0', name, NULL::varchar, population, point, topic_id, mpoly IS NOT NULL, pcode IS NOT NULL, popularity, feature_class, feature_code as subquery1 FROM appfd_place WHERE name = target AND point IS NOT NULL;
    RETURN QUERY SELECT appfd_place.id, appfd_place.admin_level, country_code, admin1_code, (SELECT rank FROM appfd_countrycoderank WHERE order_id = token AND country_code = appfd_place.country_code LIMIT 1), appfd_alias.alias || '--0', appfd_place.name, appfd_alias.alias, appfd_place.population, appfd_place.point, appfd_place.topic_id, appfd_place.mpoly IS NOT NULL, appfd_place.pcode IS NOT NULL, appfd_place.popularity, appfd_place.feature_class, appfd_place.feature_code as subquery2 FROM appfd_place INNER JOIN appfd_aliasplace on (appfd_place.id = appfd_aliasplace.place_id) INNER JOIN appfd_alias ON (appfd_aliasplace.alias_id = appfd_alias.id) WHERE appfd_place.point IS NOT NULL AND appfd_alias.alias = target;
    IF thorough THEN
        RETURN QUERY
            SELECT id, admin_level, country_code, admin1_code, code, (SELECT target || '--' || levenshtein_less_equal(target, appfd_place.name, 2))::text, name, NULL::varchar, population, point, topic_id, mpoly IS NOT NULL, pcode IS NOT NULL, popularity, feature_class, feature_code
            FROM appfd_place
            WHERE country_code = (SELECT country_code FROM appfd_countrycoderank WHERE order_id = token ORDER BY rank LIMIT 1)
            AND appfd_place.point IS NOT NULL
            AND levenshtein_less_equal(target_name, name, 2) <= 2;
    END IF;
    RETURN;
END; $$
LANGUAGE PLPGSQL;
