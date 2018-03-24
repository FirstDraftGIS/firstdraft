/* should only take about 5 minutes */
DROP TABLE IF EXISTS genesis;
CREATE TABLE genesis (
    page_id bigint,
    titles text
);
COPY genesis FROM '/tmp/genesis.tsv' WITH (FORMAT 'csv', DELIMITER E'\t')
