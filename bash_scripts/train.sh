# abort script if any problems 
set -o errexit

echo "STARTING train.sh"

sudo -Hu usrfd bash -c "source /home/usrfd/venv/bin/activate && python /home/usrfd/firstdraft/projfd/manage.py runscript ai.train"

echo "FINISHING train.sh"
