set -e

echo "running install on system requirements in case there are recent updates"
sudo DEBIAN_FRONTEND=noninteractive apt-get install -y {{system_reqs}}

echo "upgrading python packages just in case there are recent updates to requirements.txt"
sudo -H -u usrfd bash -c "cd /home/usrfd && source /home/usrfd/venv/bin/activate && /home/usrfd/venv/bin/pip install date-extractor georefdata georich location-extractor marge"

sudo service postgresql restart
echo "restarted postgresql"

echo "Creating firstdraft directory"

sudo -H -u usrfd bash -c "git clone --depth=1 https://github.com/FirstDraftGIS/firstdraft ~/firstdraft"

echo "MIGRATING"
sudo -H -u usrfd bash -c "cd /home/usrfd && source /home/usrfd/venv/bin/activate && cd firstdraft/projfd && python3 manage.py makemigrations && python3 manage.py migrate"

cd /tmp
echo "will download conformed.tsv.zip"
wget --no-verbose https://s3.amazonaws.com/firstdraftgis/conformed.tsv.zip
echo "downloaded conformed.tsv.zip"
unzip conformed.tsv.zip

echo "copying from conformed into database"
time sudo -u postgres psql -c "COPY appfd_place FROM '/tmp/conformed.tsv' WITH (FORMAT 'csv', DELIMITER E'	', HEADER, NULL '')" dbfd

sudo -H -u usrfd bash -c "echo 'DB_INDEX = True' > ~/firstdraft/projfd/projfd/dynamic_settings.py"

echo "MIGRATING"
sudo -H -u usrfd bash -c "cd /home/usrfd && source /home/usrfd/venv/bin/activate && cd firstdraft/projfd && python3 manage.py makemigrations && python3 manage.py migrate"

rm -fr /tmp/conformed.tsv*