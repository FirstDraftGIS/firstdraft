set -e

echo "starting to load training data"

# updating
sudo -H -u usrfd bash -c "cd ~/firstdraft/projfd && git pull"

cd /tmp
    echo "downloading genesis"
    time wget --no-verbose https://s3.amazonaws.com/firstdraftgis/genesis.tsv.zip
    unzip genesis.tsv.zip


echo "MIGRATING"
sudo -H -u usrfd bash -c "cd /home/usrfd && source /home/usrfd/venv/bin/activate && cd firstdraft/projfd && python3 manage.py makemigrations && python3 manage.py migrate"

# takes 2.65 hours to conform
sudo -H -u usrfd bash -c "cd /home/usrfd && source /home/usrfd/venv/bin/activate && cd firstdraft/projfd && time python3 manage.py runscript export.genesis"

rm -fr /tmp/genesis.tsv.*

sudo -H -u usrfd bash -c "mkdir -p ~/Data"

sudo -H -u usrfd bash -c "mv /tmp/firstdraftgis_export.tsv ~/Data/."