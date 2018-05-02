set -e

echo "SETTING UP APACHE" 

#http://stackoverflow.com/questions/31318068/shell-script-to-remove-a-file-if-it-already-exist
if [ -f "/var/log/apache2/*" ] ; then
    sudo rm "/var/log/apache2/*"
fi

sudo a2enmod wsgi

sudo cp /home/usrfd/firstdraft/configs/fd.conf /etc/apache2/sites-available/fd.conf
if [ -f "/etc/apache2/sites-enabled/fd.conf" ] ; then
    sudo rm /etc/apache2/sites-enabled/fd.conf
fi

sudo ln -s /etc/apache2/sites-available/fd.conf /etc/apache2/sites-enabled/fd.conf

sudo service apache2 restart
