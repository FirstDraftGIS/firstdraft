FROM ubuntu:latest

MAINTAINER First Draft GIS, LLC

WORKDIR ~/

ADD . /firstdraft

RUN apt-get -qq update

# Install add-apt-repository command and others
RUN DEBIAN_FRONTEND=noninteractive apt-get -qq install -y software-properties-common | grep -v "^[(Selecting)|(Preparing)|(Unpacking)]"

# Install System Repositories
RUN add-apt-repository -y $(awk 'NR>=3 { printf $2 " " }' firstdraft/system_repositories.md)

# make sure have links to most recent version of system packages
RUN apt-get -qq update

# install all system packages in system_requirements.md
RUN DEBIAN_FRONTEND=noninteractive apt-get -qq install -y $(awk 'NR>=3 { printf $2 " " }' firstdraft/system_requirements.md)  | grep -v "^[(Adding)|(Enabling)|(Selecting)|(Preparing)|(Unpacking)|(update-alternatives)]"

# Install Mapnik
#RUN bash firstdraft/bash_scripts/install_mapnik.sh

# set environmental variables
# so pip install works
RUN locale-gen en_US.UTF-8
ENV LANG en_US.UTF-8
ENV LANGUAGE en_US:en

# install pip
RUN curl --silent --show-error --retry 5 https://bootstrap.pypa.io/get-pip.py | python3

# just hedging incase version is old
RUN pip3 install --upgrade pip

# install all Python requirements.txt
RUN pip3 install -r firstdraft/requirements.txt

# install scikit-learn after installed numpy and scipy
RUN pip3 install -U scikit-learn

# download NLTK data
RUN python3 -c "import nltk; nltk.download('stopwords')"

RUN service postgresql restart


RUN bash firstdraft/bash_scripts/setup_database.sh

RUN psql -c "CREATE EXTENSION unaccent; CREATE EXTENSION postgis; CREATE EXTENSION postgis_topology; CREATE EXTENSION fuzzystrmatch; CREATE EXTENSION pg_trgm;" dbfd

RUN echo "Creating and Installing safecast Extension"
RUN git clone https://github.com/DanielJDufour/safecast
RUN cd safecast && make install && make installcheck
RUN psql -c "CREATE EXTENSION safecast" dbfd


RUN service postgresql restart

RUN echo "Building Database Tables"
RUN cd firstdraft/projfd && python3 manage.py makemigrations && python3 manage.py migrate

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