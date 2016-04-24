[![Build Status](https://travis-ci.org/DanielJDufour/firstdraft.svg?branch=master)](https://travis-ci.org/DanielJDufour/firstdraft)
[![Requirements Status](https://requires.io/github/DanielJDufour/firstdraft/requirements.svg?branch=master)](https://requires.io/github/DanielJDufour/firstdraft/requirements/?branch=master)
[![Hex.pm](https://img.shields.io/hexpm/l/plug.svg?maxAge=2592000?style=plastic)]()

# firstdraft
Automatically generate first drafts of maps

# Features
| Languages Supported |
| ------------------- |
| Arabic |
| English |
| Spanish|

#### Important Names
| name | thing |
| --------- | --------- |
| firstdraft | git repo |
| projfd | Django project |
| appfd | Django app |
| dbfd | database |
| usrfd | user|


#### Some Python Packages Installed 
* beautifulsoup4 is used for web scraping
* boto is used to connect with AWS
* django is the framework that runs the site
* Pillow is used by Django for ImageField
* psycopg2 connects the Django site to the database
* python-social-auth is used so people can login via Facebook, Google and other things
* Psycopg is a PostgreSQL database adapater for Python

#### Some APT Packages Installed
* apache: webserver
* apache2-dev: python_mod needs this
* apache2-mpm-prefork: unknown
* apt-file: useful for looking up which packages have which files
* autoconf: used by postgis autogen.sh
* build-essential: includes c++ compilier we need for sfcgal
* curl: download files from internet
* git: used to download code from github repositories
* postgresql: the database that stores the information
* libapache2-mod-wsgi: installed for wsgi
* libjson0...: for Json-C dependency for postgis
* libpq-dev: needed to install psycopg2 database adapater
* pkg-config: postgis dependency
* vim: used to edit files in terminal

####Create Admin User
The following command will prompt you for a username and email address.
Enter ```admin``` as username and enter your email address.
And enter your password twice.
```
python ~/firstdraft/projbkto/manage.py createsuperuser;
```
