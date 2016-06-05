echo "starting deliver_slave"

echo "slave_instance_id: $slave_instance_id"

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
image_id=$(aws ec2 create-image --instance-id $slave_instance_id --name "$name" --description "$name" | grep -P '(?<="ImageId": ")ami-[a-z\d]+(?=")' --only-matching)
echo "image_id: $image_id"

echo "waiting until image is created"
while true; do
  echo "sleeping 10 seconds"
  sleep 10
  state=$(aws ec2 describe-images --image-ids $image_id | grep -P '(?<="State": ")[a-z]*(?=")' --only-matching)
  echo "state: $state"
  if [ "$state" = "available" ]; then
    break;
  fi
done

image_id=$(aws ec2 describe-images --owners self --filters Name=name,Values="First Draft GIS" | grep -P '(?<="ImageId": ")ami-[a-z\d]+(?=")' --only-matching)
echo "image_id: $image_id"
if [ "$image_id" == "" ];then
   echo "image_id is blank"
else
    echo "image_id is NOT blank, so deregister"
    aws ec2 deregister-image --image-id $image_id
    echo "deregistered"
fi

aws ec2 terminate-instances --instance-ids $slave_instance_id



echo "finishing deliver_slave"
