set -e

sudo service postgresql restart

echo "CREATING POSTGRESQL USER AND DATABASE"
sudo -u postgres psql -c "CREATE USER usrfd;"
sudo -u postgres psql -c 'CREATE USER "www-data";'
sudo -u postgres psql -c "CREATE DATABASE dbfd;"
sudo -u postgres psql -c "ALTER DATABASE dbfd OWNER TO usrfd;"
sudo -u postgres psql -c 'GRANT ALL ON DATABASE dbfd TO "www-data";'
sudo -u postgres psql -c 'GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO "www-data";' dbfd;
sudo -u postgres psql -c 'GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO "www-data";' dbfd;
sudo -u postgres psql -c 'GRANT ALL PRIVILEGES ON ALL FUNCTIONS IN SCHEMA public TO "www-data";' dbfd;
sudo -u postgres psql -c "CREATE EXTENSION unaccent; CREATE EXTENSION postgis; CREATE EXTENSION postgis_topology; CREATE EXTENSION fuzzystrmatch; CREATE EXTENSION pg_trgm; CREATE EXTENSION safecast;" dbfd

sudo service postgresql restart

echo "SETTING POSTGRESQL CONFIG FILE"
sudo updatedb; #this is used to initialize locate command
path_to_pg_hba_conf=$(locate pg_hba.conf | grep "^/etc/postgresql/[0-9].[0-9]/main/pg_hba.conf$")
echo "path_to_pg_hba_conf: $path_to_pg_hba_conf"
cd /tmp
wget https://raw.githubusercontent.com/FirstDraftGIS/firstdraft/master/pg_hba.conf
sudo cp /tmp/pg_hba.conf $path_to_pg_hba_conf
sudo chown postgres:postgres $path_to_pg_hba_conf

sudo service postgresql restart