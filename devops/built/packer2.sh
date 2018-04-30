
# https://www.packer.io/intro/getting-started/build-image.html
# https://www.packer.io/docs/builders/amazon.html#iam-task-or-instance-role

echo "validating packer2.json"
packer validate packer2.json

packer build -var "aws_access_key=$AWS_ACCESS_KEY_ID" -var "aws_secret_key=$AWS_SECRET_ACCESS_KEY" -var "aws_owner_id=$AWS_OWNER_ID" packer2.json
