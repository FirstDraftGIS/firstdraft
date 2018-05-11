set -e

echo "running install on system requirements in case there are recent updates"
sudo DEBIAN_FRONTEND=noninteractive apt-get install -y {{system_reqs}}

echo "upgrading python packages just in case there are recent updates to requirements.txt"
sudo -H -u usrfd bash -c "cd /home/usrfd && source /home/usrfd/venv/bin/activate && /home/usrfd/venv/bin/pip install date-extractor georefdata georich location-extractor marge"

sudo service postgresql restart
echo "restarted postgresql"

cd /tmp
echo "will download conformed.tsv.zip"
wget --no-verbose https://s3.amazonaws.com/firstdraftgis/conformed.tsv.zip
echo "downloaded conformed.tsv.zip"
unzip conformed.tsv.zip