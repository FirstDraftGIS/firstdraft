# abort script if any problems 
set -o errexit

echo "STARTING clean.sh"

echo "REMOVING TERMINAL HISTORY"
history -cw
sudo -u usrfd history -cw

echo "REMOVING APACHE LOGS" 
sudo rm /var/log/apache2/*
sudo service apache2 restart

echo "FINISHING clean.sh"
