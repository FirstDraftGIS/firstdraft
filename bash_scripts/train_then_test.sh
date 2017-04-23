# abort script if any problems 
set -o errexit

echo "STARTING train_then_test.sh"

bash -c "source /home/usrfd/venv/bin/activate && python /home/usrfd/firstdraft/projfd/manage.py runscript ai.train >> /home/usrfd/firstdraft/projfd/logs/train.log"
bash -c "source /home/usrfd/venv/bin/activate && python /home/usrfd/firstdraft/projfd/manage.py runscript ai.test >> /home/usrfd/firstdraft/projfd/logs/test.log"

echo "FINISHING train_then_test.sh"
