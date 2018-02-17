# Install add-apt-repository command and others

DEBIAN_FRONTEND=noninteractive apt-get -qq install -y software-properties-common | grep -v "^[(Selecting)|(Preparing)|(Unpacking)]";