echo "starting Jenkinsfile"

node('ec2') {
  echo "starting ec2-slave"
  sh 'wget https://raw.githubusercontent.com/FirstDraftGIS/firstdraft/master/build_slave.sh -O /tmp/build_slave.sh'
  //sh 'sudo bash /tmp/build_slave.sh'
  echo "finishing ec2-slave"
}

step {
    echo "starting deliver"
    sh "aws copy-image --source-region us-east-1 --source-image-id ami-4917552c --name FDGIS"
    echo "ending deliver"
}

echo "finishing Jenkinsfile"
