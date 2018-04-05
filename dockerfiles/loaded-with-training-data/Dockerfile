FROM firstdraftgis/loaded:latest
MAINTAINER First Draft GIS, LLC
WORKDIR /
RUN cd /tmp \
 &&  wget --no-verbose https://s3.amazonaws.com/firstdraftgis/genesis.tsv.zip \
 &&  unzip genesis.tsv.zip \
 &&  rm genesis.tsv.zip
RUN rm -fr /firstdraft/projfd/appfd/scripts/conform
ADD ./projfd/appfd/scripts/conform /firstdraft/projfd/appfd/scripts/conform
RUN rm -fr /firstdraft/projfd/appfd/models
ADD ./projfd/appfd/models /firstdraft/projfd/appfd/models
RUN cd /firstdraft/projfd \
 &&  service postgresql restart \
 &&  sleep 720 \
 &&  python3 manage.py makemigrations \
 &&  python3 manage.py migrate
RUN cd /firstdraft/projfd \
 &&  service postgresql restart \
 &&  sleep 720 \
 &&  python3 manage.py runscript conform.training_data
