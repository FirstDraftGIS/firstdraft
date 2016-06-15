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

echo "LOADING COUNTRY POLYGONS"
sudo --set-home -u usrfd bash -c 'source ~/venv/bin/activate && cd ~/firstdraft/projfd && python ~/firstdraft/projfd/manage.py runscript loadLSIBWVS'

echo "LOADING MYNAMAR PCODES"
#sudo --set-home -u usrfd bash -c "source ~/venv/bin/activate && cd ~/firstdraft/projfd && python ~/firstdraft/projfd/manage.py runscript  load --script-args='https://data.hdx.rwlabs.org/dataset/myanmar-adiministrative-boundaries'"
#sudo --set-home -u usrfd bash -c "source ~/venv/bin/activate && cd ~/firstdraft/projfd && python ~/firstdraft/projfd/manage.py runscript  load --script-args='https://data.hdx.rwlabs.org/dataset/myanmar-village-boundaries'"

#sudo --set-home -u usrfd bash -c "source ~/venv/bin/activate && cd ~/firstdraft/projfd && python ~/firstdraft/projfd/manage.py runscript  load --script-args='https://data.hdx.rwlabs.org/dataset/myanmar-village-locations'"
#sudo --set-home -u usrfd bash -c "source ~/venv/bin/activate && cd ~/firstdraft/projfd && python ~/firstdraft/projfd/manage.py runscript  load --script-args='https://data.hdx.rwlabs.org/dataset/myanmar-village-boundaries'"

# to-do: figure out admin level for new towns based on looking at parent admin level and see if 100% same admin level
#sudo -Hu usrfd bash -c "cd /home/usrfd/firstdraft/projfd python manage.py runscript load --script-args='https://data.hdx.rwlabs.org/dataset/myanmar-town-locations'"
#sudo -Hu usrfd bash -c "cd /home/usrfd/firstdraft/projfd python manage.py runscript load --script-args='https://data.hdx.rwlabs.org/dataset/honduras-admin-level-1-boundaries'"


echo "FINISHING load.sh"
