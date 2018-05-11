#!/bin/bash

set -e;

echo "starting to install user requirements"

echo "CREATE SYSTEM USER usrfd"
sudo useradd usrfd -m

echo "CREATING VIRUTAL ENVIRONMENT"
sudo -H -u usrfd bash -c "cd /home/usrfd && virtualenv /home/usrfd/venv"

echo "INSTALLING PYTHON PACKAGES"
sudo -H -u usrfd bash -c "cd /home/usrfd && source /home/usrfd/venv/bin/activate && /home/usrfd/venv/bin/pip install behave-django bnlp3 bscrp beryl boto broth Cython date-extractor Django django-braces django-cors-headers django-crispy-forms djangorestframework djangorestframework-gis djangorestframework-queryfields django-rest-swagger django-extensions django-filter django-guardian django-sendfile django-timezone-field editdistance freq gensim geojson georefdata georich html5lib language-detector location-extractor lxml marge markdown maxminddb metadata-extractor mod_wsgi newspaper3k nltk numpy openpyxl pandas Pillow psycopg2-binary PyPDF2 pyproj git+git://github.com/GeospatialPython/pyshp pydash python-dateutil python-docx python-magic pyvirtualdisplay PyYAML pytz requests scipy scrp selenium six social-auth-app-django stop-words super_python table-extractor titlecase unidecode validators wheel  --upgrade"

echo "INSTALL SCIKIT LEARN"
sudo -H -u usrfd bash -c "cd /home/usrfd && source /home/usrfd/venv/bin/activate && /home/usrfd/venv/bin/pip install scikit-learn"

echo "DOWNLOAD NLTK DATA"
sudo -H -u usrfd bash -c "cd /home/usrfd && source /home/usrfd/venv/bin/activate && python3 -c \"import nltk; nltk.download('stopwords')\""
