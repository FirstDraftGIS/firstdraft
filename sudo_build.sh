#update packages
sudo apt-get update;
sudo apt-get -y dist-upgrade;
sudo apt-get install -y apache2 apache2-dev apache2-mpm-prefork apt-file build-essential cmake curl default-jdk default-jre fabric git libapache2-mod-wsgi libboost-all-dev libcgal-dev libgdal1-dev libgeos-dev libgmp3-dev libmpfr-dev libmpfr-doc libmpfr4 libmpfr4-dbg libproj-dev libpq-dev maven pgadmin3 postgresql postgresql-contrib postgresql-9.4-postgis-2.1 postgresql-server-dev-all python python-dev python-pip python-qgis python-virtualenv qgis vim xvfb

# create user
sudo useradd usrfd -m && sudo passwd usrfd;

#create database
sudo -u postgres psql -c "CREATE USER usrfd;";
sudo -u postgres psql -c "CREATE DATABASE dbfd;"
sudo -u postgres psql -c "ALTER DATABASE dbfd OWNER TO usrfd;"
sudo -u postgres psql -c "CREATE EXTENSION postgis; CREATE EXTENSION postgis_topology;" dbfd


sudo -u usrfd git clone http://github.com/danieljdufour/firstdraft.git /home/usrfd/firstdraft;
sudo -u usrfd bash -c "cd /home/usrfd && virtualenv venv;"
sudo -u usrfd bash -c "cd /home/usrfd && source venv/bin/activate && pip install -r /home/usrfd/firstdraft/requirements.txt;"

#(1) load database dump or (2) start over by migrating and loading geonames

#(2)

sudo -u usrfd bash -c "cd /home/usrfd && source venv/bin/activate && cd firstdraft/projfd && python manage.py makemigrations"
sudo -u usrfd bash -c "cd /home/usrfd && source venv/bin/activate && cd firstdraft/projfd && python manage.py migrate"

sudo wget http://download.geonames.org/export/dump/allCountries.zip -O /tmp/allCountries.zip
cd /tmp && sudo unzip allCountries.zip

# takes about 20 min an an AWS Medium EC2 Ubuntu 15.04
sudo -u postgres psql -f /home/usrfd/firstdraft/load_geonames.sql dbfd;


# add hidden.py




# enable wsgi mod in 
sudo a2enmod wsgi;

sudo cp /home/usrfd/firstdraft/fd.conf /etc/apache2/sites-available/fd.conf;
sudo ln -s /etc/apache2/sites-available/fd.conf /etc/apache2/sites-enabled/fd.conf;
sudo service apache2 restart;
