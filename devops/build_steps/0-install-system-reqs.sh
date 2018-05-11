#!/bin/bash

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
sudo DEBIAN_FRONTEND=noninteractive apt-get -q install -y apache2 apache2-dev apt-file apt-utils autoconf build-essential clang clang-3.8 cmake curl cython cython3 default-jdk default-jre g++-6 gcc gcc-6 gfortran git libapache2-mod-wsgi libatlas-base-dev libblas3 libblas-dev liblapack-dev libboost-all-dev libc6 libcgal-dev libgdal1-dev libgeos-dev libgmp3-dev liblapack3 libmpfr-dev libmpfr-doc libmpfr4 libmpfr4-dbg libopenblas-dev libproj-dev libpq-dev libxslt1-dev locales make maven osmctools pkg-config postgresql postgresql-contrib postgresql-server-dev-all ^postgresql-[0-9].[0-9]-postgis-[0-9].[0-9]$ python3 software-properties-common vim zip zlib1g-dev | grep -v '^[(Get)|(Adding)|(Enabling)|(Selecting)|(Preparing)|(Unpacking)|(update)]';
echo "installed system packages"
sudo locale-gen en_US.UTF-8
echo "ran locale-gen"
LANG=en_US.UTF-8
echo "set LANG"
LANGUAGE=en_US:en
echo "set LANGUAGE"

echo "INSTALLING PIP"
sudo curl --silent --show-error --retry 5 https://bootstrap.pypa.io/get-pip.py | sudo -H python3

echo "INSTALL virtualenv"
sudo -H pip install virtualenv

sudo git clone https://github.com/DanielJDufour/safecast /safecast
cd /safecast
sudo make install
echo "installed safecast"