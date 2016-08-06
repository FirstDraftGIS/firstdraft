# abort script if any problems 
set -o errexit

echo "STARTING load.sh"

echo "LOADING GEONAMES"
sudo rm -fr /tmp/allCountries.*
cd /tmp && wget http://download.geonames.org/export/dump/allCountries.zip --no-verbose
cd /tmp && unzip allCountries.zip
sudo python /home/usrfd/firstdraft/loadGeoNames.py

echo "Updating Primary Key Value Just In Case"
sudo -u usrfd psql -c "SELECT setval('appfd_place_id_seq', (SELECT MAX(id) FROM appfd_place)+1)" dbfd;

echo "STARTING TO LOAD AlTERNATE NAMES AT $(date)"
sudo rm -fr /tmp/alternateNames.*
cd /tmp && wget http://download.geonames.org/export/dump/alternateNames.zip --no-verbose
cd /tmp && unzip alternateNames.zip
sudo -u postgres psql -f /home/usrfd/firstdraft/sql_scripts/loadAlternateNames.sql dbfd
echo "FINISHED LOADING AlTERNATE NAMES AT $(date)"

echo "LOADING COUNTRY INFO"
sudo --set-home -u usrfd bash -c 'source ~/venv/bin/activate && cd ~/firstdraft/projfd && python ~/firstdraft/projfd/manage.py runscript loadCountryInfo -v3'

echo "LOADING COUNTRY POLYGONS"
sudo --set-home -u usrfd bash -c 'source ~/venv/bin/activate && cd ~/firstdraft/projfd && python ~/firstdraft/projfd/manage.py runscript loadLSIBWVS -v3'

echo "Updating Primary Key Value Just In Case"
sudo -u usrfd psql -c "SELECT setval('appfd_place_id_seq', (SELECT MAX(id) FROM appfd_place)+1)" dbfd;

echo "LOADING OTHER DATASETS"
sudo --set-home -u usrfd bash -c 'source ~/venv/bin/activate && cd ~/firstdraft/projfd && python ~/firstdraft/projfd/manage.py runscript loadDatasets -v3'

echo "FINISHING load.sh"
