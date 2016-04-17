[![Build Status](https://travis-ci.org/DanielJDufour/firstdraft.svg?branch=master)](https://travis-ci.org/DanielJDufour/firstdraft)
[![Requirements Status](https://requires.io/github/DanielJDufour/firstdraft/requirements.svg?branch=master)](https://requires.io/github/DanielJDufour/firstdraft/requirements/?branch=master)

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
* psycopg2 connects the Django site to the database
* python-social-auth is used so people can login via Facebook, Google and other things
* Psycopg is a PostgreSQL database adapater for Python

# Some APT Packages
* apache: webserver
* apache2-dev: python_mod needs this
* apache2-mpm-prefork: unknown
* apt-file: useful for looking up which packages have which files
* autoconf: used by postgis autogen.sh
* build-essential: includes c++ compilier we need for sfcgal
* cmake: required for sfcgal
* curl: download files from internet
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
* pkg-config: postgis dependency
* postgis: NOT INCLUDING. MUST BUILD FROM SOURCE
* postgresql-9.3-postgis-2.1: connects postgresql to postgis 
* postgresql-contrib: postgis requires it
* postgresql-server-dev-all: includes all postgres stuff needed; includes postgresql-server-dev-X.Y, which is needed to install psycopg2 database adapater
* python: code language that django uses
* python-dev:
* python-pip: is used to install python packages
* vim: used to edit files in terminal

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

##### Load Initial Data
```
python manage.py runscript loadGeoNames
python manage.py runscript loadAlternateNames
python manage.py runscript loadCountryInfo
python manage.py runscript loadLSIBWVS
python manage.py runscript load --script-args="https://data.hdx.rwlabs.org/dataset/myanmar-adiministrative-boundaries"
python manage.py runscript load --script-args="https://data.hdx.rwlabs.org/dataset/myanmar-village-boundaries"
python manage.py runscript load --script-args="https://data.hdx.rwlabs.org/dataset/myanmar-village-locations"

# to-do: figure out admin level for new towns based on looking at parent admin level and see if 100% same admin level
python manage.py runscript load --script-args="https://data.hdx.rwlabs.org/dataset/myanmar-town-locations"

python manage.py runscript load --script-args="https://data.hdx.rwlabs.org/dataset/honduras-admin-level-1-boundaries"
```
