#sudo -u usrfd git clone http://github.com/danieljdufour/firstdraft.git /home/usrfd/firstdraft;
#sudo chown usrfd:usrfd /home/usrfd/firstdraft -R;
#sudo -u usrfd bash -c "cd /home/usrfd && virtualenv venv;"
#sudo -u usrfd bash -c "cd /home/usrfd && source venv/bin/activate && pip install -r /home/usrfd/firstdraft/requirements.txt;"

#sudo -u usrfd bash -c "cd /home/usrfd && source venv/bin/activate && cd firstdraft/projfd && python manage.py makemigrations"
#sudo -u usrfd bash -c "cd /home/usrfd && source venv/bin/activate && cd firstdraft/projfd && python manage.py migrate"

#sudo wget http://download.geonames.org/export/dump/allCountries.zip -O /tmp/allCountries.zip
#cd /tmp && sudo unzip allCountries.zip

# takes about 20 min an an AWS Medium EC2 Ubuntu 15.04
#sudo -u postgres psql -f /home/usrfd/firstdraft/load_geonames.sql dbfd;

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

# create maps directory that will store maps (e.g., geojsons, shapefiles, CSV's)
#sudo -u usrfd bash -c "mkdir /home/usrfd/maps";
