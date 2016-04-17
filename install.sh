sudo DEBIAN_FRONTEND=noninteractive apt-get -y -o Dpkg::Options::="--force-confnew" install apache2 apache2-dev apache2-mpm-prefork apt-file build-essential cmake curl libapache2-mod-wsgi libboost-all-dev libcgal-dev libgdal1-dev libgeos-dev libgmp3-dev libmpfr-dev libmpfr-doc libmpfr4 libmpfr4-dbg libproj-dev libpq-dev python-qgis python-virtualenv qgis vim zip libxslt1-dev
sudo psql -U postgres -c "CREATE extension postgis"
sudo psql -U postgres -c "CREATE extension postgis_topology"
sudo psql -U postgres -c "CREATE extension fuzzystrmatch"
sudo psql -U postgres -c 'CREATE database dbfd'
sudo psql -U postgres -c 'CREATE user usrfd'
sudo psql -U postgres -c 'ALTER DATABASE dbfd OWNER TO usrfd'
sudo useradd usrfd -m
sudo -u usrfd git clone http://github.com/danieljdufour/firstdraft.git /home/usrfd/firstdraft
sudo chown usrfd:usrfd /home/usrfd/firstdraft -R
