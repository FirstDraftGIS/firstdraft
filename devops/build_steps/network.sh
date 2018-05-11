set -e

echo "running install on system requirements in case there are recent updates"
sudo DEBIAN_FRONTEND=noninteractive apt-get install -y apache2 apache2-dev apt-file apt-utils autoconf build-essential clang clang-3.8 cmake curl cython cython3 default-jdk default-jre g++-6 gcc gcc-6 gfortran git libapache2-mod-wsgi-py3 libatlas-base-dev libblas3 libblas-dev liblapack-dev libboost-all-dev libc6 libcgal-dev libgdal1-dev libgeos-dev libgmp3-dev liblapack3 libmpfr-dev libmpfr-doc libmpfr4 libmpfr4-dbg libopenblas-dev libproj-dev libpq-dev libxslt1-dev locales make maven osmctools pkg-config postgresql postgresql-contrib postgresql-server-dev-all ^postgresql-[0-9].[0-9]-postgis-[0-9].[0-9]$ python3 software-properties-common vim zip zlib1g-dev

echo "install local copy of newspaper bc pip version trying to save to /var/www/ folder"
sudo -H -u usrfd bash -c "cd /home/usrfd && source /home/usrfd/venv/bin/activate && rm -fr ~/newspaper && git clone https://github.com/codelucas/newspaper && pip install --upgrade -e ~/newspaper"

sudo -H -u usrfd bash -c "cd ~/firstdraft/projfd && git pull"

# collect static, so apache can serve CSS for DRF GUI
sudo -H -u usrfd bash -c "cd /home/usrfd && source /home/usrfd/venv/bin/activate && cd ~/firstdraft/projfd && python3 manage.py collectstatic"

# give apache2 access to new tables in db
sudo -u postgres psql -c 'GRANT ALL ON DATABASE dbfd TO "www-data";'
sudo -u postgres psql -c 'GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO "www-data";' dbfd;
sudo -u postgres psql -c 'GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO "www-data";' dbfd;
sudo -u postgres psql -c 'GRANT ALL PRIVILEGES ON ALL FUNCTIONS IN SCHEMA public TO "www-data";' dbfd;

sudo rm -fr /var/log/apache2/*

sudo a2enmod wsgi

sudo cp /home/usrfd/firstdraft/configs/fd-usrfd.conf /etc/apache2/sites-available/fd.conf

sudo rm -f /etc/apache2/sites-enabled/fd.conf

sudo ln -s /etc/apache2/sites-available/fd.conf /etc/apache2/sites-enabled/fd.conf

sudo chown -R www-data:www-data /home/usrfd/maps

sudo service apache2 restart