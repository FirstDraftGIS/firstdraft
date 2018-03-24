FROM firstdraftgis/loaded:latest
MAINTAINER First Draft GIS, LLC
WORKDIR /
RUN cd /tmp \
 &&  wget --no-verbose https://s3.amazonaws.com/firstdraftgis/genesis.tsv.zip \
 &&  unzip genesis.tsv.zip \
 &&  rm genesis.tsv.zip
RUN rm -fr /firstdraft/projfd/appfd/scripts/conform
ADD ./projfd/appfd/scripts/conform /firstdraft/projfd/appfd/scripts/conform
RUN cd /firstdraft/projfd \
 &&  service postgresql restart \
 &&  sleep 720 \
 &&  python3 manage.py runscript conform.training_data
RUN cd /firstdraft/projfd \
 &&  service postgresql restart \
 &&  sleep 720 \
 &&  psql -c "COPY appfd_order FROM '/tmp/order.tsv' WITH (FORMAT 'csv', DELIMITER E'	', HEADER, NULL '')" dbfd \
 &&  psql -c "COPY appfd_feature FROM '/tmp/feature.tsv' WITH (FORMAT 'csv', DELIMITER E'	', HEADER, NULL '')" dbfd \
 &&  psql -c "COPY appfd_feature FROM '/tmp/featureplace.tsv' WITH (FORMAT 'csv', DELIMITER E'	', HEADER, NULL '')" dbfd
RUN rm /tmp/order.tsv \
 &&  rm /tmp/feature.tsv \
 &&  rm /tmp/featureplace.tsv
