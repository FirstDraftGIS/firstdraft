set -e

echo "starting to load training data"

cd /tmp

echo "downloading genesis"
#time wget --no-verbose https://s3.amazonaws.com/firstdraftgis/genesis.tsv.zip -O genesis.tsv.zip
#time unzip -o genesis.tsv.zip
if [ -n "$fdgis_prod_build" ]; then
    rm genesis.tsv.zip
fi
rm -fr ~/firstdraft-build/projfd/appfd/scripts/conform
cp -fr ~/firstdraft/projfd/appfd/scripts/conform ~/firstdraft-build/projfd/appfd/scripts/conform

rm -fr ~/firstdraft-build/projfd/appfd/models
cp -fr ~/firstdraft/projfd/appfd/models ~/firstdraft-build/projfd/appfd/models

cd ~/firstdraft-build/projfd
    time python3 manage.py makemigrations
    time python3 manage.py migrate
    echo "conforming training data to database schema"
    
    # takes 2.65 hoursconformer
    #time python3 manage.py runscript conform.training_data

# turn off autovaccum
#sudo -u postgres psql -c "autovacuum (false);" dbfd;

sudo -u postgres psql -c "ALTER TABLE appfd_countrycoderank SET UNLOGGED;" dbfd
sudo -u postgres psql -c "ALTER TABLE appfd_style SET UNLOGGED;" dbfd
sudo -u postgres psql -c "ALTER TABLE appfd_featureplace SET UNLOGGED;" dbfd
sudo -u postgres psql -c "ALTER TABLE appfd_feature SET UNLOGGED;" dbfd
sudo -u postgres psql -c "ALTER TABLE appfd_metadataentry SET UNLOGGED;" dbfd
sudo -u postgres psql -c "ALTER TABLE appfd_metadata SET UNLOGGED;" dbfd
sudo -u postgres psql -c "ALTER TABLE appfd_source SET UNLOGGED;" dbfd
sudo -u postgres psql -c "ALTER TABLE appfd_order SET UNLOGGED;" dbfd

# takes about 1 min
time sudo -u postgres psql -c "TRUNCATE TABLE appfd_order CASCADE; COPY appfd_order FROM '/tmp/order.tsv' WITH (FORMAT 'csv', DELIMITER E'\t', HEADER, NULL '', FREEZE)" dbfd

# takes about 8 minutes
time sudo -u postgres psql -c "TRUNCATE TABLE appfd_feature CASCADE; COPY appfd_feature FROM '/tmp/feature.tsv' WITH (FORMAT 'csv', DELIMITER E'\t', HEADER, NULL '', FREEZE)" dbfd

time sudo -u postgres psql -c "TRUNCATE TABLE appfd_featureplace CASCADE; tgitCOPY appfd_featureplace FROM '/tmp/featureplace.tsv' WITH (FORMAT 'csv', DELIMITER E'\t', HEADER, NULL '', FREEZE)" dbfd

# turn on autovaccum
#sudo -u postgres psql -c "autovacuum (true);" dbfd;

if [ -n "$fdgis_prod_build" ]; then
    rm /tmp/order.tsv
    rm /tmp/feature.tsv
    rm /tmp/featureplace.tsv
fi

# upload conformed files to s3
aws s3 cp /tmp/order.tsv s3://firstdraftgis/order.tsv
aws s3 cp /tmp/feature.tsv s3://firstdraftgis/feature.tsv
aws s3 cp /tmp/featureplace.tsv s3://firstdraftgis/featureplace.tsv