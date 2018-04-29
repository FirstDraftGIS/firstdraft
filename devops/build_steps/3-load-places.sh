set -e

echo "running install on system requirements in case there are recent updates"
sudo DEBIAN_FRONTEND=noninteractive apt-get install -y apache2 apache2-dev apt-file apt-utils autoconf build-essential clang clang-3.8 cmake curl cython cython3 default-jdk default-jre g++-6 gcc gcc-6 gfortran git libapache2-mod-wsgi libatlas-base-dev libblas3 libblas-dev liblapack-dev libboost-all-dev libc6 libcgal-dev libgdal1-dev libgeos-dev libgmp3-dev liblapack3 libmpfr-dev libmpfr-doc libmpfr4 libmpfr4-dbg libopenblas-dev libproj-dev libpq-dev libxslt1-dev locales make maven osmctools pkg-config postgresql postgresql-contrib postgresql-server-dev-all ^postgresql-[0-9].[0-9]-postgis-[0-9].[0-9]$ python3 software-properties-common vim zip zlib1g-dev

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