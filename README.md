# firstdraft
Automatically generate first drafts of maps

###Installation Guide
firstdraft = name of the repository
projfd = name of the Django project
appfd = name of the Django app
dbfd = name of the database
usrfd = name of the local user

### Some Python Packages Installed 
* beautifulsoup4 is used for web scraping
* boto is used to connect with AWS
* django is the framework that runs the site
* django-tastypie is used to pass data from server to tables
* fabric is used to shh into remote servers and execute commands
* fabric-virtualenv used for using virtual environments in deployment
* fexpect is used to respond to prompts in fabric when deploying
* imagehash is used for image recognition and analysis
* pexpect is used to respond to questions in Fabric
* psycopg2 connects the Django site to the database
* python-social-auth is used so people can login via Facebook, Google and other things
* Psycopg is a PostgreSQL database adapater for Python
* python-dateutil is a dependency of Tastypie
* python-mimeparse is a dependency of Tastypie
* 

####Update and Upgrade Server
```
sudo apt-get update;
sudo apt-get -y dist-upgrade;
```


####Install Required Packages
```
sudo apt-get install -y apache2 apache2-dev apache2-mpm-prefork apt-file build-essential cmake curl default-jdk default-jre fabric git libapache2-mod-wsgi libboost-all-dev libcgal-dev libgdal1-dev libgeos-dev libgmp3-dev libmpfr-dev libmpfr-doc libmpfr4 libmpfr4-dbg libproj-dev libpq-dev maven pgadmin3 postgresql postgresql-9.3-postgis-2.1 postgresql-contrib postgresql-server-dev-all python python-dev python-pip python-qgis python-virtualenv qgis vim xvfb
```
* apache: webserver
* apache2-dev: python_mod needs this
* apache2-mpm-prefork: unknown
* apt-file: useful for looking up which packages have which files
* autoconf: used by postgis autogen.sh
* build-essential: includes c++ compilier we need for sfcgal
* cmake: required for sfcgal
* curl: download files from internet
* default-jdk: java
* default-jre: java
* fabic: ssh into remote servers and deploy them via build scripts
* git: used to download code from github repositories
* postgresql: the database that stores the information
* libapache2-mod-wsgi: installed for wsgi
* libboost-all-dev (aka boost): required for sfcgal
* libcgal-dev: required for sfcgal
* libgdal1-dev: gdal-config, file from it is required for compiling postgis from source
* libgeos-dev: it's file geos-config is required for compiling postgis from source
* libgmp3-dev (aka gmp): required for sfcgal
* libjson0...: for Json-C dependency for postgis
* libmpfr-dev libmpfr-doc libmpfr4 libmpfr4-dbg (aka mpfr): required for sfcgal
* libproj-dev: compiling postgis from source requires the file proj_api.h
* libpq-dev: needed to install psycopg2 database adapater
* maven: required for java projects
* pgadmin3: connect to gisbkto database
* pkg-config: postgis dependency
* postgis: NOT INCLUDING. MUST BUILD FROM SOURCE
* postgresql-9.3-postgis-2.1: connects postgresql to postgis 
* postgresql-contrib: postgis requires it
* postgresql-server-dev-all: includes all postgres stuff needed; includes postgresql-server-dev-X.Y, which is needed to install psycopg2 database adapater
* python: code language that django uses
* python-dev:
* python-pexpect: used for automating answer to prompts
* python-pip: is used to install python packages
* python-qgis: python bindings for qgis
* qgis: for looking at shapefiles and geojsons
* vim: used to edit files in terminal


####Create Local User
Create the user named usrfd, who will actually run the Django app.
The -m at the end tells it to create a home directory for the usrfd user.
```
sudo useradd usrfd -m && sudo passwd usrfd;
```

####Set Up Database
Create a usrfd user in the database
Create a database
Make usrfd owner of that database
```
sudo -u postgres psql -c "CREATE USER usrfd;";
sudo -u postgres psql -c "CREATE DATABASE dbfd;"
sudo -u postgres psql -c "ALTER DATABASE dbfd OWNER TO usrfd;"
sudo -u postgres psql -c "CREATE EXTENSION postgis; CREATE EXTENSION postgis_topology;" dbfd
```

####Install SFCGAL
This is used to compute where to place the label and other crazy cool stuff
```
cd ~\
curl --location --remote-name https://github.com/Oslandia/SFCGAL/archive/v1.0.tar.gz
tar xvzf v1.0.tar.gz
cd ~/SFCGAL-1.0/
cmake . && make && sudo make install
```


####Install Postgis & SFCGAL
We have to compile and install postgis from source because we have to manually configure it for SFCGAL.

```
#allow postgis to files in c
sudo -u postgres psql -c "UPDATE pg_language SET lanpltrusted = true WHERE lanname LIKE 'c';"
sudo service postgresql restart


download it
sudo ./configure --with-sfcgal=/home/usrfd/SFCGAL-1.0/sfcgal-config
make
sudo make install
sudo mkdir /home/usrfd/sfcgal
sudo cp /usr/share/postgresql/9.3/contrib/postgis-2.1/sfcgal.sql /home/usrfd/sfcgal/sfcgal.sql
sudo chown -R usrfd:usrfd /home/usrfd/sfcgal/
su usrfd
psql dbfd -f /home/usrfd/sfcgal/sfcgal.sql
```


####Change to usrfd user and it's directory
It will ask for the password, which you gave after running passwd.
```
su usrfd -p;
cd /home/usrfd;
```

####Download Most Recent Version of Django
This version will include the geojson serializer we need
```
git clone git://github.com/django/django.git /home/usrfd/django-trunk
```

####Download this repository of code
```
git clone http://github.com/danieljdufour/firstdraft.git /home/usrfd/firstdraft;
```

####Change into Repo Directory
```
cd /home/usrfd/firstdraft;
```

####Create Virtual Environment and Activate It
```
virtualenv venv;
source venv/bin/activate;
```


####Install Django
```
pip install -e /home/usrfd/django-trunk
```

####Install Python Packages
The -r lets you install python packages to usrfd's directory and not the system directory.
We add --user at the end to force everything, especially python-social-auth, to install everything under usrfd and not the system superuser.
```
pip install -r /home/usrfd/firstdraft/requirements.txt --ignore-installed;
```


####Create Tables in Database
makemigrations creates the instructions for the database
migrate actually runs those instructions
```
python ~/firstdraft/projfd/manage.py makemigrations;
python ~/firstdraft/projfd/manage.py migrate;
```

####Create Admin User
The following command will prompt you for a username and email address.
Enter ```admin``` as username and enter your email address.
And enter your password twice.
```
python ~/firstdraft/projbkto/manage.py createsuperuser;
```

####Set up WSGI
```
sudo a2enmod wsgi;
```

####Copy Over Apache2 Config File to Site-Enabled Directory
```
sudo cp /home/usrfd/firstdraft/fd.conf /etc/apache2/sites-available/fd.conf;
```

####Create Symbolic Link
```
sudo ln -s /etc/apache2/sites-available/fd.conf /etc/apache2/sites-enabled/fd.conf;
```

####Restart Apache
```
sudo service apache2 restart;
```
