set -o errexit;

echo "restarting postgresql";
service postgresql restart;

echo "changing into firstdraft/projfd";
cd firstdraft/projfd;

echo "making migrations";
python3 manage.py makemigrations;

echo "migrating";
python3 manage.py migrate;

echo "restarting postgresql";
service postgresql restart;