FROM ubuntu:latest

MAINTAINER First Draft GIS, LLC

WORKDIR /

RUN apt-get -qq update

ADD . /firstdraft

RUN bash firstdraft/bash_scripts/install_software_properties_common.sh

RUN bash firstdraft/bash_scripts/add_apt_repos.sh

RUN apt-get -qq update

RUN bash firstdraft/bash_scripts/install_system_packages.sh

#RUN bash firstdraft/bash_scripts/install_mapnik.sh

RUN bash firstdraft/bash_scripts/install_python_packages.sh

RUN bash firstdraft/bash_scripts/setup_database.sh

# make migrations
RUN cd firstdraft/projfd && python3 manage.py makemigrations

# migrate
RUN cd firstdraft/projfd && python3 manage.py migrate

RUN echo "Loading Unum Data"
RUN cd /tmp && wget https://s3.amazonaws.com/firstdraftgis/conformed.tsv.zip && unzip conformed.tsv.zip
RUN psql -f firstdraft/sql_scripts/unum/load.sql dbfd

RUN echo "Indexing Database"
RUN echo "DB_INDEX = True" >> firstdraft/projfd/projfd/dynamic_settings.py 
RUN cd firstdraft/projfd && python3 manage.py makemigrations && python3 manage.py migrate

#CREATING INDEXES AND SQL FUNCTIONS
#RUN psql -f firstdraft/sql_scripts/calc_popularity.sql dbfd
#RUN psql -f firstdraft/sql_scripts/resolve.sql dbfd

# WHERE SHOULD I Create Maps Folder???
# can I programatically generate via postgis toGeojson functionality and mapnik??

# Need to set up apache2
# can I run train on crontab in docker container??

RUN echo "finished building docker container"


EXPOSE 80


# DEBUG WITH docker run --rm -it d9e56bffd6f5 sh 