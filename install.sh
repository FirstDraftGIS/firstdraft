echo "INSTALLING APT PACKAGES"
#sudo DEBIAN_FRONTEND=noninteractive apt-get -y -o Dpkg::Options::="--force-confnew" install apache2 apache2-dev apache2-mpm-prefork apt-file build-essential cmake curl libapache2-mod-wsgi libboost-all-dev libcgal-dev libgdal1-dev libgeos-dev libgmp3-dev libmpfr-dev libmpfr-doc libmpfr4 libmpfr4-dbg libproj-dev libpq-dev python python-dev python-qgis python-virtualenv qgis vim zip libxslt1-dev

echo "CREATING DATABASE"
sudo psql -U postgres -c "CREATE extension postgis"
sudo psql -U postgres -c "CREATE extension postgis_topology"
sudo psql -U postgres -c "CREATE extension fuzzystrmatch"
sudo psql -U postgres -c 'CREATE database dbfd'
sudo psql -U postgres -c 'CREATE user usrfd'
sudo psql -U postgres -c 'ALTER DATABASE dbfd OWNER TO usrfd'

echo "CREATING user usrfd"
#Create the user named usrfd, who will actually run the Django app.
#The -m at the end tells it to create a home directory for the usrfd user.
sudo useradd usrfd -m

echo "CLONING firstdraft into /home/usrfd/firstdraft"
sudo -u usrfd git clone http://github.com/danieljdufour/firstdraft.git /home/usrfd/firstdraft
sudo chown usrfd:usrfd /home/usrfd/firstdraft -R

echo "INSTALLING PYTHON PACKAGES"
sudo -u usrfd bash -c "cd /home/usrfd && virtualenv /home/usrfd/venv"
echo "Created virtualenv at ls /home/usrfd"
ls -alsh /home/usrfd
ls -alsh /home/usrfd/firstdraft
sudo -u usrfd bash -c "cd /home/usrfd && source /home/usrfd/venv/bin/activate && pip install -r /home/usrfd/firstdraft/requirements.txt;"

echo "CREATING TABLES"
sudo -u usrfd bash -c "cd /home/usrfd && source venv/bin/activate && cd firstdraft/projfd && python manage.py makemigrations"
sudo -u usrfd bash -c "cd /home/usrfd && source venv/bin/activate && cd firstdraft/projfd && python manage.py migrate"

# create maps directory that will store maps (e.g., geojsons, shapefiles, CSV's)
sudo -u usrfd bash -c "mkdir /home/usrfd/maps";
