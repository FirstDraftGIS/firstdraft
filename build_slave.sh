echo "STARTING build_slave.sh"

sudo DEBIAN_FRONTEND=noninteractive apt-get -y -o Dpkg::Options::="--force-confnew" update

# commented this out because updating linux headers takes too long.. should just change AMI instead
#sudo DEBIAN_FRONTEND=noninteractive apt-get -y -o Dpkg::Options::="--force-confnew" dist-upgrade

echo "INSTALLING SYSTEM PACKAGES"
sudo DEBIAN_FRONTEND=noninteractive apt-get -y -o Dpkg::Options::="--force-confnew" install apache2 apache2-dev apache2-mpm-prefork apt-file build-essential cmake curl default-jdk default-jre fabric git libapache2-mod-wsgi libboost-all-dev libcgal-dev libgdal1-dev libgeos-dev libgmp3-dev libmpfr-dev libmpfr-doc libmpfr4 libmpfr4-dbg libproj-dev libpq-dev maven nodejs npm postgresql postgresql-contrib postgresql-server-dev-all postgresql-9.3-postgis-2.1 python python-dev python-pip python-qgis python-virtualenv qgis vim xvfb zip libxslt1-dev

sudo npm install npm -g;
# if node command not found link it to existing nodejs command
if [ ! -f /usr/bin/node ]; then sudo ln -s /usr/bin/nodejs /usr/bin/node; fi


echo "SETTING UP DATABASE"
sudo service postgresql restart
sudo -u postgres psql -c "CREATE USER usrfd;";
sudo -u postgres psql -c "CREATE DATABASE dbfd;"
sudo -u postgres psql -c "ALTER DATABASE dbfd OWNER TO usrfd;"
sudo -u postgres psql -c "CREATE EXTENSION postgis; CREATE EXTENSION postgis_topology; CREATE EXTENSION fuzzystrmatch;" dbfd

echo "CREATE USER usrfd"
if [ -z "$(getent passwd usrfd)" ]; then sudo useradd usrfd -m; fi

if [ ! -d /home/usrfd/firstdraft ]; then
  echo "CLONING firstdraft into /home/usrfd/firstdraft"
  sudo -H -u usrfd bash -c "cd /home/usrfd && git clone https://github.com/FirstDraftGIS/firstdraft.git";
fi

if [ ! -d /home/usrfd/venv ]; then
  echo "CREATING VIRUTAL ENVIRONMENT"
  sudo -H -u usrfd bash -c "cd /home/usrfd && virtualenv /home/usrfd/venv"
fi

echo "INSTALLING PYTHON PACKAGES"
sudo -H -u usrfd bash -c "cd /home/usrfd && source /home/usrfd/venv/bin/activate && /home/usrfd/venv/bin/pip install -r /home/usrfd/firstdraft/requirements.txt"

echo "CREATING TABLES"
sudo -Hu usrfd bash -c "source /home/usrfd/venv/bin/activate && python /home/usrfd/firstdraft/projfd/manage.py makemigrations"
sudo -Hu usrfd bash -c "source /home/usrfd/venv/bin/activate && python /home/usrfd/firstdraft/projfd/manage.py migrate"

echo "CREATING MAPS FOLDER"
if [ ! -d /home/usrfd/maps ]; then
  sudo -u usrfd bash -c "mkdir /home/usrfd/maps";
fi

echo "FINISHING build_slave.sh"
