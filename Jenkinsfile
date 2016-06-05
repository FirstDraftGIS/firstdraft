echo "starting Jenkinsfile"

def slave_name = ""

node('ec2') {
  echo "starting ec2-slave"
  slave_name = env.NODE_NAME
  sh 'wget https://raw.githubusercontent.com/FirstDraftGIS/firstdraft/master/build_slave.sh -O /tmp/build_slave.sh'
  echo "finishing ec2-slave"
}

slave_instance_id = slave_name.find(/i\-[a-z\d]+/)

node('master') {
    echo "starting deliver"
    sh "whoami"
    sh "aws ec2 stop-instances --instance-ids " + slave_instance_id
    sleep 10
    sh "aws ec2 create-image --instance-id " + slave_instance_id + " --name 'FDGIS' --description 'First Draft GIS' --region us-east-1"
    
    //keep sleeping until ami is describe as available
    //sh "while aws ec2 describe-images --image-ids " + slave_instance_id
    sh "while true; do "
    + " echo 'sleeping 10 seconds';"
    + " sleep 10;"
    + " state=$(aws ec2 describe-images --image-ids ami-48aa5425 | grep -P '(?<=\"State\": \")[a-z]*(?=\")' --only-matching);"
    + " if '$state' == 'available'; then break;"
    + " done;"
    sh "aws ec2 terminate-instances --dry-run --instance-ids " + slave_instance_id
    
    echo "ending deliver"
}

echo "finishing Jenkinsfile"
