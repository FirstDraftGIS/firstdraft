set -e

mkdir -p ~/maps

cd ~/
    rm -fr ~/marge
    git clone https://github.com/FirstDraftGIS/marge
    sudo pip install -e ~/marge

    rm -fr ~/georich
    git clone https://github.com/DanielJDufour/georich
    sudo pip install -e ~/georich
    

cd ~/Data
    wget https://s3.amazonaws.com/firstdraftgis/cooccurrences.pickle.zip
    unzip cooccurrences.pickle.zip

cd ~/marge/marge
    python3 split.py
    python3 train.py