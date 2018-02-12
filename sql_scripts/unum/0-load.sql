/* takes about 7 minutes */
COPY appfd_place FROM '/tmp/conformed.tsv' WITH (FORMAT 'csv', DELIMITER E'\t', HEADER, NULL '');

UPDATE appfd_place SET name_normalized = unaccent(lower(name_ascii));
