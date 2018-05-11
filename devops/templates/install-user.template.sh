#!/bin/bash

set -e;

echo "starting to install user requirements"

echo "CREATE SYSTEM USER usrfd"
sudo useradd usrfd -m

echo "CREATING VIRUTAL ENVIRONMENT"
sudo -H -u usrfd bash -c "cd /home/usrfd && virtualenv /home/usrfd/venv"

echo "INSTALLING PYTHON PACKAGES"
sudo -H -u usrfd bash -c "cd /home/usrfd && source /home/usrfd/venv/bin/activate && /home/usrfd/venv/bin/pip install {{python_reqs}} --upgrade"

echo "INSTALL SCIKIT LEARN"
sudo -H -u usrfd bash -c "cd /home/usrfd && source /home/usrfd/venv/bin/activate && /home/usrfd/venv/bin/pip install scikit-learn"

echo "DOWNLOAD NLTK DATA"
sudo -H -u usrfd bash -c "cd /home/usrfd && source /home/usrfd/venv/bin/activate && python3 -c \"import nltk; nltk.download('stopwords')\""
