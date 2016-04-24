echo "STARTING build_slave.sh"

sudo DEBIAN_FRONTEND=noninteractive apt-get -y -o Dpkg::Options::="--force-confnew" update

# commented this out because updating linux headers takes too long.. should just change AMI instead
#sudo DEBIAN_FRONTEND=noninteractive apt-get -y -o Dpkg::Options::="--force-confnew" dist-upgrade

echo "INSTALLING SYSTEM PACKAGES"
sudo DEBIAN_FRONTEND=noninteractive apt-get -y -o Dpkg::Options::="--force-confnew" install apache2 apache2-dev apache2-mpm-prefork apt-file build-essential cmake curl default-jdk default-jre fabric git libapache2-mod-wsgi libboost-all-dev libcgal-dev libgdal1-dev libgeos-dev libgmp3-dev libmpfr-dev libmpfr-doc libmpfr4 libmpfr4-dbg libproj-dev libpq-dev maven nodejs npm postgresql postgresql-contrib postgresql-server-dev-all '^postgresql-[0-9].[0-9]-postgis-[0-9].[0-9]$' python python-dev python-pip python-qgis python-virtualenv qgis vim xvfb zip libxslt1-dev

sudo npm install npm -g;
# if node command not found link it to existing nodejs command
if [ ! -f /usr/bin/node ]; then sudo ln -s /usr/bin/nodejs /usr/bin/node; fi

echo "SETTING UP DATABASE"
sudo service postgresql restart
sudo -u postgres psql -c "CREATE USER usrfd;";
sudo -u postgres psql -c "CREATE DATABASE dbfd;"
sudo -u postgres psql -c "ALTER DATABASE dbfd OWNER TO usrfd;"
sudo -u postgres psql -c "CREATE EXTENSION postgis; CREATE EXTENSION postgis_topology; CREATE EXTENSION fuzzystrmatch;" dbfd

echo "DELETE USER"
# wipes the slates clean
sudo deluser --remove-all-files usrfd

echo "CREATE USER usrfd"
sudo useradd usrfd -m

echo "CLONING firstdraft into /home/usrfd/firstdraft"
sudo -H -u usrfd bash -c "cd /home/usrfd && git clone https://github.com/FirstDraftGIS/firstdraft.git";

echo "CREATING VIRUTAL ENVIRONMENT"
sudo -H -u usrfd bash -c "cd /home/usrfd && virtualenv /home/usrfd/venv"

echo "INSTALLING PYTHON PACKAGES"
sudo -H -u usrfd bash -c "cd /home/usrfd && source /home/usrfd/venv/bin/activate && /home/usrfd/venv/bin/pip install -r /home/usrfd/firstdraft/requirements.txt --upgrade"

echo "CREATING TABLES"
sudo -Hu usrfd bash -c "source /home/usrfd/venv/bin/activate && python /home/usrfd/firstdraft/projfd/manage.py makemigrations"
sudo -Hu usrfd bash -c "source /home/usrfd/venv/bin/activate && python /home/usrfd/firstdraft/projfd/manage.py migrate"

echo "CREATING MAPS FOLDER"
sudo -u usrfd bash -c "mkdir /home/usrfd/maps"

echo "LOADING GEONAMES"
cd /tmp && wget http://download.geonames.org/export/dump/allCountries.zip
cd /tmp && unzip allCountries.zip
date
#sudo -u postgres psql -f /home/usrfd/firstdraft/load_geonames.sql dbfd
echo "about to load"
sudo cat /home/usrfd/firstdraft/projfd/appfd/scripts/loadGeoNames.py
sudo -Hu usrfd bash -c "source /home/usrfd/venv/bin/activate && python /home/usrfd/firstdraft/projfd/manage.py runscript loadGeoNames"
echo "loaded"
date

echo "SETTING UP APACHE" 
sudo a2enmod wsgi
sudo cp /home/usrfd/firstdraft/fd.conf /etc/apache2/sites-available/fd.conf
sudo ln -s /etc/apache2/sites-available/fd.conf /etc/apache2/sites-enabled/fd.conf
sudo service apache2 restart

echo "FINISHING build_slave.sh"
