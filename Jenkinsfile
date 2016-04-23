echo "starting Jenkinsfile"

node('ec2') {
  echo "starting ec2-slave"
  sh 'wget https://raw.githubusercontent.com/FirstDraftGIS/firstdraft/master/build_slave.sh -O /tmp/build_slave.sh'
  sh 'sudo bash /tmp/build_slave.sh'
  echo "finishing ec2-slave"
}

echo "finishing Jenkinsfile"
