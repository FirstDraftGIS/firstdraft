FROM ubuntu:latest

MAINTAINER First Draft GIS, LLC

WORKDIR /

ADD . /firstdraft

# make sure have links to most recent version of system packages
RUN apt-get update

# install all system packages in system_requirements.md
RUN apt-get install -y $(awk 'NR>=3 { printf $2 " " }' firstdraft/system_requirements.md)

# set environmental variables
# so pip install works
RUN locale-gen en_US.UTF-8
ENV LANG en_US.UTF-8
ENV LANGUAGE en_US:en

# install pip
RUN curl --silent --show-error --retry 5 https://bootstrap.pypa.io/get-pip.py | python3

# just hedging incase version is old
RUN pip install --upgrade pip

# install all Python requirements.txt
RUN pip install -r firstdraft/requirements.txt

# install scikit-learn after installed numpy and scipy
RUN pip install -U scikit-learn

RUN git clone -b python-2-head https://github.com/DanielJDufour/newspaper.git
RUN pip install -e newspaper
# need to reinstall six with upgrade because newspaper will install old version
RUN pip install --upgrade six
#https://stackoverflow.com/questions/38447738/beautifulsoup-html5lib-module-object-has-no-attribute-base
RUN pip install html5lib==0.9999999

# download NLTK data
RUN python3 -c "import nltk; nltk.download('stopwords')"

RUN service postgresql restart

RUN psql -c "CREATE DATABASE dbfd;"

RUN psql -c "CREATE EXTENSION unaccent; CREATE EXTENSION postgis; CREATE EXTENSION postgis_topology; CREATE EXTENSION fuzzystrmatch; CREATE EXTENSION pg_trgm;" dbfd
RUN git clone https://github.com/DanielJDufour/safecast
RUN cd safecast && make install && make installcheck
RUN psql -c "CREATE EXTENSION safecast" dbfd


RUN service postgresql restart

RUN cd firstdraft/projfd && python3 manage.py makemigrations
RUN cd firstdraft/projfd && python3 manage.py migrate

RUN echo "Loading Unum Data"
RUN cd /tmp && wget https://s3.amazonaws.com/firstdraftgis/conformed.tsv.zip && unzip conformed.tsv.zip
RUN psql -f firstdraft/sql_scripts/unum/load.sql dbfd

#CREATING INDEXES AND SQL FUNCTIONS
RUN psql -f firstdraft/sql_scripts/calc_popularity.sql dbfd
RUN psql -f firstdraft/sql_scripts/resolve.sql dbfd

# WHERE SHOULD I Create Maps Folder???
# can I programatically generate via postgis toGeojson functionality and mapnik??

# Need to set up apache2
# can I run train on crontab in docker container??

RUN echo "finished building docker container"


EXPOSE 80
