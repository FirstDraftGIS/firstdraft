COPY appfd_alternatename FROM '/tmp/alternateNames.txt' DELIMITER E'\t'
DROP INDEX IF EXISTS alternatename_index;
CREATE INDEX alternatename_index ON appfd_alternatename (alternate_name);
