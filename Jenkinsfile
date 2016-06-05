echo "starting Jenkinsfile"

node('ec2') {
  echo "starting ec2-slave"
  sh 'wget https://raw.githubusercontent.com/FirstDraftGIS/firstdraft/master/build_slave.sh -O /tmp/build_slave.sh'
  //sh 'sudo bash /tmp/build_slave.sh'
  sh "curl http://169.254.169.254/latest/meta-data/instance-id"
  echo "finishing ec2-slave"
}

node {
    echo "starting deliver"
    //sh "aws ec2 "
    //sh "aws ec2 copy-image --source-region us-east-1 --source-image-id ami-4917552c --name FDGIS --region us-east-1"
    //sh "aws ec2 create-image --instance-id --name 'FDGIS' --description 'First Draft GIS'
    echo "ending deliver"
}

echo "finishing Jenkinsfile"
