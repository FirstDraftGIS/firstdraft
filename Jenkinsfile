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
    sh "aws ec2 create-image --instance-id " + slave_instance_id + " --name 'FDGIS' --description 'First Draft GIS' --region us-east-1"
    echo "ending deliver"
}

echo "finishing Jenkinsfile"
