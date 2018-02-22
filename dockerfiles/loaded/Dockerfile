FROM fdgis/base:latest
MAINTAINER First Draft GIS, LLC
WORKDIR /
RUN service postgresql restart \
 &&  su postgres -c "psql -c 'CREATE DATABASE dbfd'" \
 &&  su postgres -c "psql -c 'CREATE ROLE $(whoami) SUPERUSER LOGIN CREATEDB'" \
 &&  su postgres -c "psql -c 'ALTER DATABASE dbfd OWNER TO $(whoami)'"
RUN service postgresql restart \
 &&  psql -c 'CREATE EXTENSION unaccent; CREATE EXTENSION postgis; CREATE EXTENSION postgis_topology; CREATE EXTENSION fuzzystrmatch; CREATE EXTENSION pg_trgm; CREATE EXTENSION safecast;' dbfd
ADD . /firstdraft
RUN cd /firstdraft/projfd \
 &&  service postgresql restart \
 &&  python3 manage.py makemigrations \
 &&  python3 manage.py migrate
ADD ../links/conformed.tsv /tmp
