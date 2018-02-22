FROM ubuntu:latest
MAINTAINER First Draft GIS, LLC
WORKDIR /
RUN apt-get -qq update
RUN DEBIAN_FRONTEND=noninteractive apt-get -qq install -y software-properties-common | grep -v "^[(Selecting)|(Preparing)|(Unpacking)]";
RUN add-apt-repository -y ppa:ubuntu-toolchain-r/test
RUN add-apt-repository -y ppa:deadsnakes/ppa
RUN apt-get -qq update
RUN DEBIAN_FRONTEND=noninteractive apt-get -q install -y apache2 apache2-dev apt-file apt-utils autoconf build-essential clang clang-3.8 cmake curl cython cython3 default-jdk default-jre g++-6 gcc gcc-6 gfortran git libapache2-mod-wsgi libatlas-base-dev libblas3 libblas-dev liblapack-dev libboost-all-dev libc6 libcgal-dev libgdal1-dev libgeos-dev libgmp3-dev liblapack3 libmpfr-dev libmpfr-doc libmpfr4 libmpfr4-dbg libopenblas-dev libproj-dev libpq-dev libxslt1-dev locales make maven osmctools pkg-config postgresql postgresql-contrib postgresql-server-dev-all ^postgresql-[0-9].[0-9]-postgis-[0-9].[0-9]$ python3.6 software-properties-common vim zip zlib1g-dev | grep -v '^[(Get)|(Adding)|(Enabling)|(Selecting)|(Preparing)|(Unpacking)|(update)]';
RUN locale-gen en_US.UTF-8
ENV LANG en_US.UTF-8
ENV LANGUAGE en_US:en
RUN git clone https://github.com/mapnik/mapnik --depth 10
WORKDIR /mapnik
RUN git submodule update --init
RUN bash bootstrap.sh
RUN ./configure CUSTOM_CXXFLAGS='-D_GLIBCXX_USE_CXX11_ABI=0' CXX='clang++-3.8' CC='clang-3.8' | grep -v 'yes$'
RUN make | grep -v 'clang++-3.8'
RUN make test
RUN make install | grep -v '^Install File:'
WORKDIR /
RUN curl --silent --show-error --retry 5 https://bootstrap.pypa.io/get-pip.py | python3
RUN pip3 install --upgrade pip
RUN pip3 install --quiet behave-django bnlp3 bscrp beryl boto broth Cython date-extractor Django django-braces django-crispy-forms djangorestframework djangorestframework-gis djangorestframework-queryfields django-rest-swagger django-extensions django-filter django-guardian django-sendfile django-timezone-field editdistance gensim geojson georefdata html5lib language-detector location-extractor lxml markdown maxminddb metadata-extractor mod_wsgi newspaper3k nltk numpy openpyxl pandas Pillow psycopg2-binary PyPDF2 pyproj git+git://github.com/GeospatialPython/pyshp pydash python-dateutil python-docx python-magic pyvirtualdisplay PyYAML pytz requests scipy scrp selenium six social-auth-app-django stop-words super_python table-extractor tensorflow titlecase validators wheel
RUN pip3 install -U scikit-learn
RUN python3 -c "import nltk; nltk.download('stopwords')"
RUN git clone https://github.com/DanielJDufour/safecast safecast
RUN cd /safecast && make install
