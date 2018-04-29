#!/bin/sh

set -e;

echo "starting to install dependencies"

sudo apt-get -qq update
echo "updated for the first time"
sudo apt-get install -y software-properties-common | grep -v "^[(Selecting)|(Preparing)|(Unpacking)]"
echo "installed"
sudo add-apt-repository -y ppa:ubuntu-toolchain-r/test
echo "added ubuntu-toolchain-r/test"
sudo apt-get -qq update
echo "updated for the second time"
sudo DEBIAN_FRONTEND=noninteractive apt-get -q install -y {{system_reqs}} | grep -v '^[(Get)|(Adding)|(Enabling)|(Selecting)|(Preparing)|(Unpacking)|(update)]';
echo "installed system packages"
sudo locale-gen en_US.UTF-8
echo "ran locale-gen"
LANG=en_US.UTF-8
echo "set LANG"
LANGUAGE=en_US:en
echo "set LANGUAGE"

echo "installing Python packages"
cd /
sudo curl --silent --show-error --retry 5 https://bootstrap.pypa.io/get-pip.py | sudo -H python3
echo "installed pip"
sudo -H pip install --upgrade pip
echo "upgraded pip if necessary"
sudo -H pip install --quiet {{python_reqs}}
echo "installed first pass of python packages"
sudo -H pip install -U scikit-learn
echo "installed scikit-learn"
sudo -H python3 -c "import nltk; nltk.download('stopwords')"
echo "downloaded nltk data"

sudo git clone https://github.com/DanielJDufour/safecast /safecast
cd /safecast
sudo make install
echo "installed safecast"