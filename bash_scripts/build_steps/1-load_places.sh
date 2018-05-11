set -e

echo "starting to load places"

sudo service postgresql restart
echo "restarted postgresql"

sudo -u postgres psql -c "DROP DATABASE IF EXISTS dbfd";
sudo -u postgres psql -c "CREATE DATABASE dbfd";

# don't want to delete because maybe used by someone else
if [ ! $(sudo -u postgres psql -tAc "SELECT 1 FROM pg_roles WHERE rolname='$(whoami)'") ]
then
    sudo -u postgres psql -c "CREATE ROLE $(whoami) SUPERUSER LOGIN CREATEDB"
fi

sudo -u postgres psql -c "ALTER DATABASE dbfd OWNER TO $(whoami)"
sudo -u postgres psql -c "CREATE EXTENSION unaccent; CREATE EXTENSION postgis; CREATE EXTENSION postgis_topology; CREATE EXTENSION fuzzystrmatch; CREATE EXTENSION pg_trgm; CREATE EXTENSION safecast; CREATE EXTENSION pg_bulkload;" dbfd

cd /tmp
wget --no-verbose https://s3.amazonaws.com/firstdraftgis/conformed.tsv.zip
unzip conformed.tsv.zip

echo "Creating firstdraft-build directory"
sudo git clone --depth=1 https://github.com/FirstDraftGIS/firstdraft ~/firstdraft
cd ~/firstdraft/projfd
    source ~/venv/bin/activate
        python3 manage.py makemigrations
        python3 manage.py migrate
    deactivate
    echo "copying from conformed into database"
    time sudo -u postgres psql -c "COPY appfd_place FROM '/tmp/conformed.tsv' WITH (FORMAT 'csv', DELIMITER E'	', HEADER, NULL '')" dbfd
    echo 'DB_INDEX = True' > ~/firstdraft/projfd/projfd/dynamic_settings.py
    source ~/venv/bin/activate
        python3 manage.py makemigrations
        python3 manage.py migrate
    deactivate

rm /tmp/conformed.tsv*
