# abort script if any problems 
set -o errexit

echo "starting save as user"
whoami

echo "In agent, agent_instance_id: $agent_instance_id"

echo "finishing save"
