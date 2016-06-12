echo "Starting test_agent.sh

echo "running behave tests"
sudo --set-home -u usrfd bash -c 'source ~/venv/bin/activate && cd ~/firstdraft/projfd && python ~/firstdraft/projfd/manage.py behave --use-existing-database'

echo "Finishing test_agent.sh
