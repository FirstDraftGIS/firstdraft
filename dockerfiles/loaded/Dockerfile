FROM firstdraftgis/base:latest
MAINTAINER First Draft GIS, LLC
WORKDIR /
RUN service postgresql restart \
 &&  su postgres -c "psql -c 'CREATE DATABASE dbfd'" \
 &&  su postgres -c "psql -c 'CREATE ROLE $(whoami) SUPERUSER LOGIN CREATEDB'" \
 &&  su postgres -c "psql -c 'ALTER DATABASE dbfd OWNER TO $(whoami)'"
RUN service postgresql restart \
 &&  psql -c 'CREATE EXTENSION unaccent; CREATE EXTENSION postgis; CREATE EXTENSION postgis_topology; CREATE EXTENSION fuzzystrmatch; CREATE EXTENSION pg_trgm; CREATE EXTENSION safecast;' dbfd
RUN cd /tmp \
 &&  wget --no-verbose https://s3.amazonaws.com/firstdraftgis/conformed.tsv.zip \
 &&  unzip conformed.tsv.zip \
 &&  rm conformed.tsv.zip
ADD . /firstdraft
RUN cd /firstdraft/projfd \
 &&  service postgresql restart \
 &&  python3 manage.py makemigrations \
 &&  python3 manage.py migrate
RUN service postgresql restart \
 &&  sleep 5 \
 &&  psql -c "COPY appfd_place FROM '/tmp/conformed.tsv' WITH (FORMAT 'csv', DELIMITER E'	', HEADER, NULL '')" dbfd
RUN service postgresql restart \
 &&  sleep 5 \
 &&  psql -c "UPDATE appfd_place SET name_normalized = unaccent(lower(name_ascii))" dbfd
