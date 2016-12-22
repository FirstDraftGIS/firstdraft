# abort script if any problems 
set -o errexit

echo "STARTING clean.sh"

echo "REMOVING TERMINAL HISTORY"
history -cw
echo "removed root terminal history"
sudo -u usrfd history -cw
echo "removed usrfd terminal history"

echo "REMOVING APACHE LOGS" 
sudo rm /var/log/apache2/*
sudo service apache2 restart

echo "FINISHING clean.sh"
