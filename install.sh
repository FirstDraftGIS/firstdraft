echo "INSTALLING APT PACKAGES"
sudo DEBIAN_FRONTEND=noninteractive apt-get -y -o Dpkg::Options::="--force-confnew" install apache2 apache2-dev apache2-mpm-prefork apt-file build-essential cmake curl libapache2-mod-wsgi libboost-all-dev libcgal-dev libgdal1-dev libgeos-dev libgmp3-dev libmpfr-dev libmpfr-doc libmpfr4 libmpfr4-dbg libproj-dev libpq-dev python python-dev python-qgis python-virtualenv qgis vim zip libxslt1-dev

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
sudo -H -u usrfd bash -c "cd /home/usrfd && git clone https://github.com/DanielJDufour/firstdraft.git"
echo ""
echo "/home/usrfd/firstdraft is"
ls -alsh /home/usrfd/firstdraft
echo ""
echo ""
sudo -H chown usrfd:usrfd /home/usrfd/firstdraft -R

echo "INSTALLING PYTHON PACKAGES"
sudo -H -u usrfd bash -c "cd /home/usrfd && virtualenv /home/usrfd/venv"
#sudo -H -u usrfd bash -c "cd /home/usrfd && source /home/usrfd/venv/bin/activate && /home/usrfd/venv/bin/pip install -r /home/usrfd/firstdraft/requirements.txt --root /home/usrfd/venv --install-option="--prefix='/home/usrfd/venv/local'""
sudo -H -u usrfd bash -c "cd /home/usrfd && source /home/usrfd/venv/bin/activate && /home/usrfd/venv/bin/pip install -r /home/usrfd/firstdraft/requirements.txt -vvv"

echo "CREATING TABLES"
sudo -u usrfd bash -c "cd /home/usrfd && source venv/bin/activate && cd firstdraft/projfd && python manage.py makemigrations"
sudo -u usrfd bash -c "cd /home/usrfd && source venv/bin/activate && cd firstdraft/projfd && python manage.py migrate"

# create maps directory that will store maps (e.g., geojsons, shapefiles, CSV's)
sudo -u usrfd bash -c "mkdir /home/usrfd/maps";
