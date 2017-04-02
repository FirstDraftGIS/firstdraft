CREATE OR REPLACE FUNCTION calc_popularity(placeid int)
RETURNS int AS $$
DECLARE
    plus int;
    negative int;
BEGIN
    plus := (SELECT count(appfd_featureplace.id)::int FROM appfd_featureplace INNER JOIN appfd_feature ON (appfd_featureplace.feature_id = appfd_feature.id) WHERE appfd_feature.verified = true AND appfd_featureplace.correct = true AND appfd_featureplace.place_id = placeid);
    negative := (SELECT count(appfd_featureplace.id)::int FROM appfd_featureplace INNER JOIN appfd_feature ON (appfd_featureplace.feature_id = appfd_feature.id) WHERE appfd_feature.verified = true AND appfd_featureplace.correct = false AND appfd_featureplace.place_id = placeid);
    return plus - negative;
END; $$
LANGUAGE PLPGSQL;
