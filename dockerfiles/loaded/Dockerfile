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
RUN mkdir /firstdraft
ADD ./projfd /firstdraft/projfd
RUN cd /firstdraft/projfd \
 &&  service postgresql restart \
 &&  sleep 10 \
 &&  python3 manage.py makemigrations \
 &&  python3 manage.py migrate
RUN service postgresql restart \
 &&  sleep 5 \
 &&  psql -c "COPY appfd_place FROM '/tmp/conformed.tsv' WITH (FORMAT 'csv', DELIMITER E'	', HEADER, NULL '')" dbfd
RUN cd firstdraft/projfd \
 &&  sleep 10 \
 &&  service postgresql restart \
 &&  echo 'DB_INDEX = True' >> projfd/dynamic_settings.py \
 &&  sleep 360 \
 &&  cat /var/log/postgresql/postgresql-9.5-main.log \
 &&  python3 manage.py makemigrations \
 &&  python3 manage.py migrate
RUN rm /tmp/conformed.tsv
