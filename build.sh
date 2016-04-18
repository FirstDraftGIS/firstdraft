echo "STARTING build.sh"
# commenting out this loading geonames stuff now because free travis ci doens't have enough memory
#cd /tmp && wget http://download.geonames.org/export/dump/allCountries.zip
#cd /tmp && unzip allCountries.zip
# takes about 20 min an an AWS Medium EC2 Ubuntu 15.04
#sudo -Hu postgres psql -f /home/usrfd/firstdraft/load_geonames.sql dbfd;

#python manage.py runscript loadGeoNames
#python manage.py runscript loadAlternateNames
#python manage.py runscript loadCountryInfo
#python manage.py runscript loadLSIBWVS
sudo -Hu usrfd bash -c "cd /home/usrfd/firstdraft/projfd python manage.py runscript load --script-args='https://data.hdx.rwlabs.org/dataset/myanmar-adiministrative-boundaries'"
#sudo -Hu usrfd bash -c "cd /home/usrfd/firstdraft/projfd python manage.py runscript load --script-args='https://data.hdx.rwlabs.org/dataset/myanmar-village-boundaries'"
#sudo -Hu usrfd bash -c "cd /home/usrfd/firstdraft/projfd python manage.py runscript load --script-args='https://data.hdx.rwlabs.org/dataset/myanmar-village-locations'"
# to-do: figure out admin level for new towns based on looking at parent admin level and see if 100% same admin level
#sudo -Hu usrfd bash -c "cd /home/usrfd/firstdraft/projfd python manage.py runscript load --script-args='https://data.hdx.rwlabs.org/dataset/myanmar-town-locations'"
#sudo -Hu usrfd bash -c "cd /home/usrfd/firstdraft/projfd python manage.py runscript load --script-args='https://data.hdx.rwlabs.org/dataset/honduras-admin-level-1-boundaries'"

#sudo wget http://download.geonames.org/export/dump/alternateNames.zip
#cd /tmp && sudo unzip alternateNames.zip

#sudo -u postgres psql -f /home/usrfd/firstdraft/load_alternate_names.sql dbfd;


#sudo wget http://data.openaddresses.io/openaddresses-collected.zip
#cd /tmp && sudo unzip openaddresses-collected.zip
# add hidden.py

# add md5 auth for usrfd to /etc/postgresql/9.4/main/pg_hba.conf
#sudo service postgresql restart
#sudo -u postgres psql -c "ALTER ROLE usrfd WITH PASSWORD 'passwordhere'"

# enable wsgi mod in 
#sudo a2enmod wsgi;

#sudo cp /home/usrfd/firstdraft/fd.conf /etc/apache2/sites-available/fd.conf;
#sudo ln -s /etc/apache2/sites-available/fd.conf /etc/apache2/sites-enabled/fd.conf;
#sudo service apache2 restart;


# add useful aliases
#echo "alias a='sudo su usrfd'" >> ~/.bashrc
#echo "alias m='sudo -u usrfd bash -c\"m\"'" >> ~/.bashrc
#. ~/.bashrc

#sudo -u usrfd bash -c "echo \"alias a='cd /home/usrfd && source venv/bin/activate && cd /home/usrfd/firstdraft/projfd'\" && . /home/usrfd/.bashrc"
#sudo -u usrfd bash -c "echo \"alias m='cd /home/usrfd && source venv/bin/activate && cd /home/usrfd/firstdraft/projfd && python manage.py makemigrations && python manage.py migrate'\" >> /home/usrfd/.bashrc && . /home/usrfd/.bashrc"
#sudo -u usrfd bash -c "echo \"alias s='cd /home/usrfd && source venv/bin/activate && cd /home/usrfd/firstdraft/projfd && python manage.py shell'\" && . /home/usrfd/.bashrc"


echo "FINISHING build.sh"
