set -e

echo "running install on system requirements in case there are recent updates"
sudo DEBIAN_FRONTEND=noninteractive apt-get install -y {{system_reqs}}

echo "installing all python packages just in case there are recent updates to requirements.txt"
sudo -H pip install --upgrade date-extractor georefdata georich location-extractor marge

echo "starting to load places"

sudo service postgresql restart
echo "restarted postgresql"

sudo -u postgres psql -c "DROP DATABASE IF EXISTS dbfd";
echo "dropped dbfd if necessary"
sudo -u postgres psql -c "CREATE DATABASE dbfd";
echo "created dbfd"
sudo -u postgres psql -c "CREATE ROLE $(whoami) SUPERUSER LOGIN CREATEDB"
sudo -u postgres psql -c "ALTER DATABASE dbfd OWNER TO $(whoami)"
sudo -u postgres psql -c "CREATE EXTENSION unaccent; CREATE EXTENSION postgis; CREATE EXTENSION postgis_topology; CREATE EXTENSION fuzzystrmatch; CREATE EXTENSION pg_trgm; CREATE EXTENSION safecast;" dbfd

cd /tmp
echo "will download conformed.tsv.zip"
wget --no-verbose https://s3.amazonaws.com/firstdraftgis/conformed.tsv.zip
echo "downloaded conformed.tsv.zip"
unzip conformed.tsv.zip

echo "Creating firstdraft directory"
git clone --depth=1 https://github.com/FirstDraftGIS/firstdraft ~/firstdraft
cd ~/firstdraft/projfd
python3 manage.py makemigrations
python3 manage.py migrate
echo "copying from conformed into database"
time sudo -u postgres psql -c "COPY appfd_place FROM '/tmp/conformed.tsv' WITH (FORMAT 'csv', DELIMITER E'	', HEADER, NULL '')" dbfd
echo 'DB_INDEX = True' > ~/firstdraft/projfd/projfd/dynamic_settings.py
python3 manage.py makemigrations
python3 manage.py migrate


rm -fr /tmp/conformed.tsv*