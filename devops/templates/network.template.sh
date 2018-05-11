set -e

echo "running install on system requirements in case there are recent updates"
sudo DEBIAN_FRONTEND=noninteractive apt-get install -y {{system_reqs}}

echo "install local copy of newspaper bc pip version trying to save to /var/www/ folder"
sudo -H -u usrfd bash -c "cd /home/usrfd && source /home/usrfd/venv/bin/activate && rm -fr ~/newspaper && git clone https://github.com/codelucas/newspaper && pip install --upgrade -e ~/newspaper"

sudo -H -u usrfd bash -c "cd ~/firstdraft/projfd && git pull"

sudo rm -fr /var/log/apache2/*

sudo a2enmod wsgi

sudo cp /home/usrfd/firstdraft/configs/fd-usrfd.conf /etc/apache2/sites-available/fd.conf

sudo rm -f /etc/apache2/sites-enabled/fd.conf

sudo ln -s /etc/apache2/sites-available/fd.conf /etc/apache2/sites-enabled/fd.conf

sudo service apache2 restart