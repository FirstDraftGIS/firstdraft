set -e

echo "starting to load training data"

cd /tmp
    echo "downloading genesis"
    time wget --no-verbose https://s3.amazonaws.com/firstdraftgis/genesis.tsv.zip
    unzip genesis.tsv.zip

cd /firstdraft/projfd
    time python3 manage.py makemigrations
    time python3 manage.py migrate
    echo "conforming training data to database schema"
    
    # takes 2.65 hours to conform
    time python3 manage.py runscript export.genesis
    
rm -fr /tmp/genesis.tsv.*