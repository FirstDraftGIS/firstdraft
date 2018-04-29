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
sudo DEBIAN_FRONTEND=noninteractive apt-get -q install -y apache2 apache2-dev apt-file apt-utils autoconf build-essential clang clang-3.8 cmake curl cython cython3 default-jdk default-jre g++-6 gcc gcc-6 gfortran git libapache2-mod-wsgi libatlas-base-dev libblas3 libblas-dev liblapack-dev libboost-all-dev libc6 libcgal-dev libgdal1-dev libgeos-dev libgmp3-dev liblapack3 libmpfr-dev libmpfr-doc libmpfr4 libmpfr4-dbg libopenblas-dev libproj-dev libpq-dev libxslt1-dev locales make maven osmctools pkg-config postgresql postgresql-contrib postgresql-server-dev-all ^postgresql-[0-9].[0-9]-postgis-[0-9].[0-9]$ python3 software-properties-common vim zip zlib1g-dev | grep -v '^[(Get)|(Adding)|(Enabling)|(Selecting)|(Preparing)|(Unpacking)|(update)]';
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
sudo -H pip install --quiet behave-django bnlp3 bscrp beryl boto broth Cython date-extractor Django django-braces django-cors-headers django-crispy-forms djangorestframework djangorestframework-gis djangorestframework-queryfields django-rest-swagger django-extensions django-filter django-guardian django-sendfile django-timezone-field editdistance freq gensim geojson georefdata georich html5lib language-detector location-extractor lxml marge markdown maxminddb metadata-extractor mod_wsgi newspaper3k nltk numpy openpyxl pandas Pillow psycopg2-binary PyPDF2 pyproj git+git://github.com/GeospatialPython/pyshp pydash python-dateutil python-docx python-magic pyvirtualdisplay PyYAML pytz requests scipy scrp selenium six social-auth-app-django stop-words super_python table-extractor titlecase unidecode validators wheel 
echo "installed first pass of python packages"
sudo -H pip install -U scikit-learn
echo "installed scikit-learn"
sudo -H python3 -c "import nltk; nltk.download('stopwords')"
echo "downloaded nltk data"

sudo git clone https://github.com/DanielJDufour/safecast /safecast
cd /safecast
sudo make install
echo "installed safecast"