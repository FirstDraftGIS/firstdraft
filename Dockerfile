FROM ubuntu:latest

MAINTAINER First Draft GIS, LLC

WORKDIR /

ADD . /firstdraft

RUN apt-get -qq update

# Install add-apt-repository command and others
RUN bash firstdraft/bash_scripts/install_software_properties_common.sh

# Install System Repositories
RUN bash /firstdraft/bash_scripts/add_apt_repos.sh

# make sure have links to most recent version of system packages
RUN apt-get -qq update

# install all system packages in system_requirements.md
RUN bash /firstdraft/bash_scripts/install_system_packages.sh

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
RUN pip3 install -r /firstdraft/requirements.txt

# install scikit-learn after installed numpy and scipy
RUN pip3 install -U scikit-learn

# download NLTK data
RUN python3 -c "import nltk; nltk.download('stopwords')"

RUN bash /firstdraft/bash_scripts/setup_database.sh

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