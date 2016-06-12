echo "STARTING build_agent.sh"

sudo DEBIAN_FRONTEND=noninteractive apt-get -y -o Dpkg::Options::="--force-confnew" update

# commented this out because updating linux headers takes too long.. should just change AMI instead
#sudo DEBIAN_FRONTEND=noninteractive apt-get -y -o Dpkg::Options::="--force-confnew" dist-upgrade

echo "INSTALLING SYSTEM PACKAGES"
sudo DEBIAN_FRONTEND=noninteractive apt-get -y -o Dpkg::Options::="--force-confnew" install apache2 apache2-dev apache2-mpm-prefork apt-file build-essential cmake curl default-jdk default-jre fabric gcc gfortran git libapache2-mod-wsgi libblas3 libboost-all-dev libc6 libcgal-dev libgdal1-dev libgeos-dev libgmp3-dev liblapack3 libmpfr-dev libmpfr-doc libmpfr4 libmpfr4-dbg libproj-dev libpq-dev maven nodejs npm postgresql postgresql-contrib postgresql-server-dev-all '^postgresql-[0-9].[0-9]-postgis-[0-9].[0-9]$' python python-dev python-pip python-qgis python-virtualenv qgis vim xvfb zip libxslt1-dev

echo "INSTALLING PYTHON PACKAGES"
sudo pip install django

sudo npm install npm -g;
# if node command not found link it to existing nodejs command
if [ ! -f /usr/bin/node ]; then sudo ln -s /usr/bin/nodejs /usr/bin/node; fi

echo "SETTING UP DATABASE"
sudo service postgresql restart

echo "RESETING POSTGRESQL TO DEFAULT CONDITIONS"
sudo -u postgres psql -c "DROP DATABASE IF EXISTS dbfd;"
sudo -u postgres psql -c "DROP ROLE IF EXISTS usrfd;"
sudo -u postgres psql -c 'DROP ROLE IF EXISTS "www-data";'

echo "CREATING POSTGRESQL USER AND DATABASE"
sudo -u postgres psql -c "CREATE USER usrfd;";
sudo -u postgres psql -c 'CREATE USER "www-data";'
sudo -u postgres psql -c "CREATE DATABASE dbfd;"
sudo -u postgres psql -c "ALTER DATABASE dbfd OWNER TO usrfd;"
sudo -u postgres psql -c 'GRANT ALL ON DATABASE dbfd TO "www-data";'
sudo -u postgres psql -c 'GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO "www-data";' dbfd;
sudo -u postgres psql -c 'GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO "www-data";' dbfd;
sudo -u postgres psql -c 'GRANT ALL PRIVILEGES ON ALL FUNCTIONS IN SCHEMA public TO "www-data";' dbfd;
sudo -u postgres psql -c "CREATE EXTENSION postgis; CREATE EXTENSION postgis_topology; CREATE EXTENSION fuzzystrmatch;" dbfd

echo "DELETE SYSTEM USER"
sudo pkill -u usrfd
sudo deluser usrfd --force --remove-home
sudo deluser --group usrfd

echo "CREATE SYSTEM USER usrfd"
sudo useradd usrfd -m

echo "CLONING firstdraft into /home/usrfd/firstdraft"
sudo -H -u usrfd bash -c "cd /home/usrfd && git clone https://github.com/FirstDraftGIS/firstdraft.git";

echo "COPY PostgreSQL Configuration FILE pg_hba.conf"
path_to_pg_hba_conf=$(locate pg_hba.conf | grep "^/etc/postgresql/[0-9].[0-9]/main/pg_hba.conf$")
sudo cp /home/usrfd/firstdraft/pg_hba.conf $path_to_pg_hba_conf
sudo chown postgres:postgres $path_to_pg_hba_conf
sudo service postgresql restart

echo "CREATING VIRUTAL ENVIRONMENT"
sudo -H -u usrfd bash -c "cd /home/usrfd && virtualenv /home/usrfd/venv"

echo "INSTALLING PYTHON PACKAGES"
sudo -H -u usrfd bash -c "cd /home/usrfd && source /home/usrfd/venv/bin/activate && /home/usrfd/venv/bin/pip install -r /home/usrfd/firstdraft/requirements.txt --upgrade"

echo "CREATING TABLES"
sudo -Hu usrfd bash -c "source /home/usrfd/venv/bin/activate && python /home/usrfd/firstdraft/projfd/manage.py makemigrations"
sudo -Hu usrfd bash -c "source /home/usrfd/venv/bin/activate && python /home/usrfd/firstdraft/projfd/manage.py migrate"

echo "UPDATE DATABASE PERMISSIONS TO ACCOUNT FOR MIGRATIONS"
sudo -u postgres psql -c 'GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO "www-data";' dbfd;
sudo -u postgres psql -c 'GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO "www-data";' dbfd;
sudo -u postgres psql -c 'GRANT ALL PRIVILEGES ON ALL FUNCTIONS IN SCHEMA public TO "www-data";' dbfd;

echo "CREATING MAPS FOLDER"
sudo -u usrfd bash -c "mkdir /home/usrfd/maps"
sudo chown "www-data":"www-data" -R /home/usrfd/maps

echo "LOADING GEONAMES"
sudo rm -fr /tmp/allCountries.*
cd /tmp && wget http://download.geonames.org/export/dump/allCountries.zip --no-verbose
cd /tmp && unzip allCountries.zip
sudo python /home/usrfd/firstdraft/loadGeoNames.py

echo "SETTING UP APACHE" 
sudo a2enmod wsgi
sudo cp /home/usrfd/firstdraft/fd.conf /etc/apache2/sites-available/fd.conf
sudo rm /etc/apache2/sites-enabled/fd.conf
sudo ln -s /etc/apache2/sites-available/fd.conf /etc/apache2/sites-enabled/fd.conf
sudo service apache2 restart

echo "FINISHING build_agent.sh"
