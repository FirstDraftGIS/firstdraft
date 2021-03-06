set -e

echo "running install on system requirements in case there are recent updates"
sudo DEBIAN_FRONTEND=noninteractive apt-get install -y apache2 apache2-dev apt-file apt-utils autoconf build-essential clang clang-3.8 cmake curl cython cython3 default-jdk default-jre g++-6 gcc gcc-6 gfortran git libapache2-mod-wsgi-py3 libatlas-base-dev libblas3 libblas-dev liblapack-dev libboost-all-dev libc6 libcgal-dev libgdal1-dev libgeos-dev libgmp3-dev liblapack3 libmpfr-dev libmpfr-doc libmpfr4 libmpfr4-dbg libopenblas-dev libproj-dev libpq-dev libxslt1-dev locales make maven osmctools pkg-config postgresql postgresql-contrib postgresql-server-dev-all ^postgresql-[0-9].[0-9]-postgis-[0-9].[0-9]$ python3 software-properties-common vim zip zlib1g-dev

echo "upgrading python packages just in case there are recent updates to requirements.txt"
sudo -H -u usrfd bash -c "cd /home/usrfd && source /home/usrfd/venv/bin/activate && /home/usrfd/venv/bin/pip install date-extractor georefdata georich location-extractor marge"

sudo service postgresql restart
echo "restarted postgresql"

echo "Creating firstdraft directory"

sudo -H -u usrfd bash -c "git clone --depth=1 https://github.com/FirstDraftGIS/firstdraft ~/firstdraft"

echo "MIGRATING"
sudo -H -u usrfd bash -c "cd /home/usrfd && source /home/usrfd/venv/bin/activate && cd firstdraft/projfd && python3 manage.py makemigrations && python3 manage.py migrate"

cd /tmp
echo "will download conformed.tsv.zip"
wget --no-verbose https://s3.amazonaws.com/firstdraftgis/conformed.tsv.zip
echo "downloaded conformed.tsv.zip"
unzip conformed.tsv.zip

echo "copying from conformed into database"
time sudo -u postgres psql -c "COPY appfd_place FROM '/tmp/conformed.tsv' WITH (FORMAT 'csv', DELIMITER E'	', HEADER, NULL '')" dbfd

sudo -H -u usrfd bash -c "echo 'DB_INDEX = True' > ~/firstdraft/projfd/projfd/dynamic_settings.py"

echo "MIGRATING"
sudo -H -u usrfd bash -c "cd /home/usrfd && source /home/usrfd/venv/bin/activate && cd firstdraft/projfd && python3 manage.py makemigrations && python3 manage.py migrate"

rm -fr /tmp/conformed.tsv*