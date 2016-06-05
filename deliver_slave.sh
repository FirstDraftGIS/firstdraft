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




description="First Draft GIS cut at `date +%Y-%m-%dT%H:%M:%S`"
image_id=$(aws ec2 create-image --instance-id $slave_instance_id --name 'FirstDraftGIS' --description $description | grep -P '(?<="ImageId": ")ami-[a-z]*(?=")' --only-matching
echo "image_id: $image_id"

echo "waiting until image is created in order to terminate"
while true; do
  echo "sleeping 10 seconds"
  sleep 10
  state=$(aws ec2 describe-images --image-ids $image_id | grep -P '(?<="State": ")[a-z]*(?=")' --only-matching)
  echo "state: $state"
  if "$state" == "available"; then
    break;
  fi
done

aws ec2 terminate-instances --dry-run --instance-ids $slave_instance_id

echo "finishing deliver_slave"
