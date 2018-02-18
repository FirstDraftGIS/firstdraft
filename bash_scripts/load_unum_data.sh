service postgresql restart;

cd /tmp;

wget --no-verbose https://s3.amazonaws.com/firstdraftgis/conformed.tsv.zip;

unzip conformed.tsv.zip


echo "changing back to previous directory"
cd -

psql -f firstdraft/sql_scripts/unum/load.sql dbfd

echo "DB_INDEX = True" >> firstdraft/projfd/projfd/dynamic_settings.py 

cd firstdraft/projfd

python3 manage.py makemigrations

python3 manage.py migrate

cd -

service postgresql restart;