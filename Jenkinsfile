echo "starting Jenkinsfile"

node('ec2') {
  echo "starting ec2-slave"
  sh 'wget https://raw.githubusercontent.com/FirstDraftGIS/firstdraft/master/sudo_build.sh -O /tmp/sudo_build.sh'
  sh 'ls -alsh /tmp'
  sh './build_slave.sh'
  echo "finishing ec2-slave"
}

echo "finishing Jenkinsfile"
