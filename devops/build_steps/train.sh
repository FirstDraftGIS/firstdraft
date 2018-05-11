set -e

echo "MIGRATING"
sudo -H -u usrfd bash -c "mkdir -p ~/maps"

echo "install local copy of marge"
sudo -H -u usrfd bash -c "cd /home/usrfd && source /home/usrfd/venv/bin/activate && rm -fr ~/marge && git clone https://github.com/FirstDraftGIS/marge && pip install -e ~/marge"

echo "install local copy of georich"
sudo -H -u usrfd bash -c "cd /home/usrfd && source /home/usrfd/venv/bin/activate && rm -fr ~/georich && git clone https://github.com/DanielJDufour/georich && pip install -e ~/georich"


cd /tmp
    wget https://s3.amazonaws.com/firstdraftgis/cooccurrences.pickle.zip
    unzip cooccurrences.pickle.zip

sudo -H -u usrfd bash -c "cp /tmp/cooccurrences.pickle ~/Data/."

sudo -H -u usrfd bash -c "cd /home/usrfd && source /home/usrfd/venv/bin/activate && cd ~/marge/marge && python3 split.py && python3 train.py"