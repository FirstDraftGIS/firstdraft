# abort script if any problems 
set -o errexit

echo "STARTING load.sh"

echo "LOADING GEONAMES"
sudo rm -fr /tmp/allCountries.*
cd /tmp && wget http://download.geonames.org/export/dump/allCountries.zip --no-verbose
cd /tmp && unzip allCountries.zip
sudo python /home/usrfd/firstdraft/loadGeoNames.py

echo "LOADING COUNTRY INFO"
sudo --set-home -u usrfd bash -c 'source ~/venv/bin/activate && cd ~/firstdraft/projfd && python ~/firstdraft/projfd/manage.py runscript loadCountryInfo'


echo "FINISHING load.sh"
