# abort script if any problems 
set -o errexit

echo "starting save"

echo "agent_instance_id: $agent_instance_id"

# install awscli which allows us to run commands that start with aws
pip install --upgrade --user awscli

function wait_until_image_is_created {
  echo "starting wait_until_image_is_created with $1"
  while true; do
    echo "    sleeping 15 seconds"
    sleep 15
    state=$(aws ec2 describe-images --image-ids $1 | grep -P '(?<="State": ")[a-z]*(?=")' --only-matching)
    echo "    state: $state"
    if [ "$state" = "available" ]; then
      break;
    fi
  done
  echo "finishing wait_until_image_is_created"
}

aws ec2 stop-instances --instance-ids $agent_instance_id

echo "waiting to make image until stopped"
while true; do
  echo "    sleeping 15 seconds"
  sleep 15
  status=$(aws ec2 describe-instance-status --instance-ids  $agent_instance_id --include-all-instances)
  echo "    status: $status"
  if [[ $status == *"stopped"* ]]; then
    break;
  fi
done
echo "instance $agent_instance_id is stopped"


name="FDGIS_`date +%Y_%m_%d_%H_%M_%S`"
echo "name: $name"
description="First Draft GIS cut at `date +%Y-%m-%dT%H:%M:%S`"
echo "description: $description"
description=name
image_id=$(aws ec2 create-image --instance-id $agent_instance_id --name "$name" --description "$description" | grep -P '(?<="ImageId": ")ami-[a-z\d]+(?=")' --only-matching)
echo "image_id: $image_id"

wait_until_image_is_created $image_id

echo "finishing save"
