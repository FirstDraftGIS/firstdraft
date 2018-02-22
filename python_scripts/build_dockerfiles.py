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

df2.write_line("ADD . /firstdraft")

# set up database tables
commands = [
    "cd /firstdraft/projfd",
    "service postgresql restart",
    "python3 manage.py makemigrations",
    "python3 manage.py migrate"]
df2.run_together(commands)

if isfile("/tmp/conformed.tsv"):
    df2.write_line("ADD ../links/conformed.tsv /tmp")
else:
    # download unum gazetteer data
    df2.run_together([
        "cd /tmp",
        "wget --no-verbose https://s3.amazonaws.com/firstdraftgis/conformed.tsv.zip",
        "unzip conformed.tsv.zip"
    ])
    
"""
# load unum gazetteer data
df.run_together([
    "service postgresql restart",
    "sleep 5", # playing it safe and making sure postgresql has restarted
    "psql -f firstdraft/sql_scripts/unum/load.sql dbfd",
])

# index database
df.run_together([
    "cd firstdraft/projfd",
    "service postgresql restart",
    "echo 'DB_INDEX = True' >> projfd/dynamic_settings.py",
    "python3 manage.py makemigrations",
    "python3 manage.py migrate",
    "service postgresql restart"
])

# will set up apache stuff in a separate build process
# this docker file is just to test and build
# so can upload db dump, model and approve code
# expose port so can make calls to server
df.write_line("EXPOSE 8000")
"""