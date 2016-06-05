echo "starting deliver_slave"

echo "slave_instance_id: $slave_instance_id"

function wait_until_image_is_created {
  echo "starting wait_until_image_is_created with $1"
  while true; do
    echo "    sleeping 10 seconds"
    sleep 10
    state=$(aws ec2 describe-images --image-ids $1 | grep -P '(?<="State": ")[a-z]*(?=")' --only-matching)
    echo "    state: $state"
    if [ "$state" = "available" ]; then
      break;
    fi
  done
  echo "finishing wait_until_image_is_created"
}

aws ec2 stop-instances --instance-ids $slave_instance_id

echo "figuring out version by lookin at previous one"

echo "waiting to make image until stopped"
while true; do
  echo "sleeping 10 seconds"
  sleep 10
  status=$(aws ec2 describe-instance-status --instance-ids  $slave_instance_id --include-all-instances)
  echo "status: $status"
  if [[ $status == *"stopped"* ]]; then
    break;
  fi
done
echo "instance $slave_instance_id is stopped"


name="FDGIS_`date +%Y_%m_%d_%H_%M_%S`"
echo "name: $name"
description="First Draft GIS cut at `date +%Y-%m-%dT%H:%M:%S`"
echo "description: $description"
description=name
image_id=$(aws ec2 create-image --instance-id $slave_instance_id --name "$name" --description "$description" | grep -P '(?<="ImageId": ")ami-[a-z\d]+(?=")' --only-matching)
echo "image_id: $image_id"


wait_until_image_is_created $image_id

echo "deleting instance because we do not need that anymore"
aws ec2 terminate-instances --instance-ids $slave_instance_id
echo "terminated $slave_instance_id"

id_of_image_to_deregister=$(aws ec2 describe-images --owners self --filters Name=name,Values="First Draft GIS" | grep -P '(?<="ImageId": ")ami-[a-z\d]+(?=")' --only-matching)
echo "id_of_image_to_deregister: $id_of_image_to_deregister"
if [ "$id_of_image_to_deregister" == "" ];then
   echo "id_of_image_to_deregister is blank"
else
    echo "id_of_image_to_deregister is NOT blank, so deregister"
    aws ec2 deregister-image --image-id $id_of_image_to_deregister
    echo "deregistered"
fi

id_of_public_image=$(aws ec2 copy-image --source-region "us-east-1" --source-image-id "$image_id" --name "First Draft GIS" --description "First Draft GIS automatically creates maps" | grep -P '(?<="ImageId": ")ami-[a-z\d]+(?=")' --only-matching)
echo "id_of_public_image: $id_of_public_image"


wait_until_image_is_created $id_of_public_image
echo "Making ami public, so everyone can launch First Draft GIS"
aws ec2 modify-image-attribute --image-id $id_of_public_image --launch-permission "{\"Add\":[{\"Group\":\"all\"}]}"



echo "finishing deliver_slave"
