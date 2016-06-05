echo "starting Jenkinsfile"

def SLAVE_NAME = ""

node('ec2') {
  echo "starting ec2-slave"
  SLAVE_NAME = env.NODE_NAME
  sh 'wget https://raw.githubusercontent.com/FirstDraftGIS/firstdraft/master/build_slave.sh -O /tmp/build_slave.sh'
  echo "finishing ec2-slave"
}

node('master') {
    echo "starting deliver"
    //sh "aws ec2 "
    //sh "aws ec2 copy-image --source-region us-east-1 --source-image-id ami-4917552c --name FDGIS --region us-east-1"
    //sh "aws ec2 create-image --instance-id --name 'FDGIS' --description 'First Draft GIS'
    echo "ending deliver"
}

print("SLAVE_NAME: " + SLAVE_NAME)

echo "finishing Jenkinsfile"
