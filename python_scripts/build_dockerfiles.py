from os.path import isfile
from re import search
from shutil import copyfile
from subprocess import check_output

from dockerfile import Dockerfile

def get_first_column_values(filepath):
    values = []
    passed_header = False if filepath.endswith(".md") else True
    with open(filepath) as f:
        for line in f:
            line = line.strip()
            if line:
                if line.count("-") > 10:
                    passed_header = True
                elif passed_header:
                    value = next(part.strip() for part in line.split("|") if part.strip())
                    values.append(value)
    return values

df1 = Dockerfile("dockerfiles/base/Dockerfile")
df1.write_line("FROM ubuntu:latest")
df1.write_line("MAINTAINER First Draft GIS, LLC")
df1.write_line("WORKDIR /")
df1.run("apt-get -qq update")
df1.run("""DEBIAN_FRONTEND=noninteractive apt-get -qq install -y software-properties-common | grep -v "^[(Selecting)|(Preparing)|(Unpacking)]";""")
for repo in get_first_column_values("system_repositories.md"):
    df1.run("add-apt-repository -y " + repo + "")
df1.run("apt-get -qq update")
reqs = " ".join(get_first_column_values("system_requirements.md"))
df1.run("DEBIAN_FRONTEND=noninteractive apt-get -q install -y " + reqs + " | grep -v '^[(Get)|(Adding)|(Enabling)|(Selecting)|(Preparing)|(Unpacking)|(update)]';")
df1.run("locale-gen en_US.UTF-8")
df1.write_line("ENV LANG en_US.UTF-8")
df1.write_line("ENV LANGUAGE en_US:en")

# install mapnik
df1.run("git clone https://github.com/mapnik/mapnik --depth 10")
df1.write_line("WORKDIR /mapnik")
df1.run("git submodule update --init")
df1.run("bash bootstrap.sh")
df1.run("./configure CUSTOM_CXXFLAGS='-D_GLIBCXX_USE_CXX11_ABI=0' CXX='clang++-3.8' CC='clang-3.8' | grep -v 'yes$'")
df1.run("make | grep -v 'clang++-3.8'")
df1.run("make test")
df1.run("make install | grep -v '^Install File:'")
df1.write_line("WORKDIR /")

# install python packages
df1.run("curl --silent --show-error --retry 5 https://bootstrap.pypa.io/get-pip.py | python3")
df1.run("pip3 install --upgrade pip")
reqs = get_first_column_values("requirements.txt")
df1.run("pip3 install --quiet " + " ".join(reqs))
df1.run("pip3 install -U scikit-learn")
df1.run('''python3 -c "import nltk; nltk.download('stopwords')"''')

# install safecast
df1.run("git clone https://github.com/DanielJDufour/safecast safecast")
df1.run("cd /safecast && make install")


###############################################################################
###############################################################################
###############################################################################

# build second docker file
df2 = Dockerfile("dockerfiles/loaded/Dockerfile")
df2.write_line("FROM firstdraftgis/base:latest")
df2.write_line("MAINTAINER First Draft GIS, LLC")
df2.write_line("WORKDIR /")

# Create Database
df2.run_together([
    "service postgresql restart",
    '''su postgres -c "psql -c 'CREATE DATABASE dbfd'"''',
    '''su postgres -c "psql -c 'CREATE ROLE $(whoami) SUPERUSER LOGIN CREATEDB'"''',
    '''su postgres -c "psql -c 'ALTER DATABASE dbfd OWNER TO $(whoami)'"'''    
])

# Create Extensions for Database
extensions = get_first_column_values("postgresql_extensions.md")
psql_command = " ".join(["CREATE EXTENSION " + ext + ";" for ext in extensions])
df2.run_together([
    "service postgresql restart",
    "psql -c '" + psql_command + "' dbfd"
])

# download place data
df2.run_together([
    "cd /tmp",
    "wget --no-verbose https://s3.amazonaws.com/firstdraftgis/conformed.tsv.zip",
    "unzip conformed.tsv.zip",
    "rm conformed.tsv.zip"
])

df2.run("mkdir /firstdraft")
df2.write_line("ADD ./projfd /firstdraft/projfd")

# set up database tables
commands = [
    "cd /firstdraft/projfd",
    "service postgresql restart",
    "sleep 10",
    "python3 manage.py makemigrations",
    "python3 manage.py migrate"]
df2.run_together(commands)


# load unum gazetteer data
df2.run_together([
    "service postgresql restart",
    "sleep 5", # playing it safe and making sure postgresql has restarted
    '''psql -c "COPY appfd_place FROM '/tmp/conformed.tsv' WITH (FORMAT 'csv', DELIMITER E'\t', HEADER, NULL '')" dbfd'''
])

# index database
df2.run_together([
    "cd firstdraft/projfd",
    "sleep 10",
    "service postgresql restart",
    "echo 'DB_INDEX = True' >> projfd/dynamic_settings.py",
    "sleep 360",
    "cat /var/log/postgresql/postgresql-9.5-main.log",
    "python3 manage.py makemigrations",
    "python3 manage.py migrate"
])

# delete conformed.tsv reducing size of docker container
df2.run("rm /tmp/conformed.tsv")


###############################################################
###############################################################
###############################################################

df3 = Dockerfile("dockerfiles/loaded-with-training-data/Dockerfile")
df3.write_line("FROM firstdraftgis/loaded:latest")
df3.write_line("MAINTAINER First Draft GIS, LLC")
df3.write_line("WORKDIR /")

# download training data
df3.run_together([
    "cd /tmp",
    "wget --no-verbose https://s3.amazonaws.com/firstdraftgis/genesis.tsv.zip",
    "unzip genesis.tsv.zip",
    "rm genesis.tsv.zip"
])

# delete and read conform script in case there were any updates
df3.run("rm -fr /firstdraft/projfd/appfd/scripts/conform")
df3.write_line("ADD ./projfd/appfd/scripts/conform /firstdraft/projfd/appfd/scripts/conform")

# delete and rerun migrations in case there were any updates
df3.run("rm -fr /firstdraft/projfd/appfd/models")
df3.write_line("ADD ./projfd/appfd/models /firstdraft/projfd/appfd/models")
df3.run_together([
    "cd /firstdraft/projfd",
    "service postgresql restart",
    "sleep 720",
    "python3 manage.py makemigrations",
    "python3 manage.py migrate"
])

# build tsvs of db tables
df3.run_together([
    "cd /firstdraft/projfd",
    "service postgresql restart",
    "sleep 720",
    "python3 manage.py runscript conform.training_data"
])

"""
df3.run_together([
    "cd /firstdraft/projfd",
    "service postgresql restart",
    "sleep 720",    
    '''psql -c "COPY appfd_order FROM '/tmp/order.tsv' WITH (FORMAT 'csv', DELIMITER E'\t', HEADER, NULL '')" dbfd''',
    '''psql -c "COPY appfd_feature FROM '/tmp/feature.tsv' WITH (FORMAT 'csv', DELIMITER E'\t', HEADER, NULL '')" dbfd''',
    '''psql -c "COPY appfd_featureplace FROM '/tmp/featureplace.tsv' WITH (FORMAT 'csv', DELIMITER E'\t', HEADER, NULL '')" dbfd''',
    "rm /tmp/order.tsv",
    "rm /tmp/feature.tsv",
    "rm /tmp/featureplace.tsv"    
])
"""

# upload tables to s3