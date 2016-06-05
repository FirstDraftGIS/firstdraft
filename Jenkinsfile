echo "starting Jenkinsfile"

def slave_name = ""

node('ec2') {
  echo "starting ec2-slave"
  slave_name = env.NODE_NAME
  sh 'wget https://raw.githubusercontent.com/FirstDraftGIS/firstdraft/master/build_slave.sh -O /tmp/build_slave.sh'
  //sh 'sudo bash /tmp/build_slave.sh'
  echo "finishing ec2-slave"
}

slave_instance_id = slave_name.find(/i\-[a-z\d]+/)

node('master') {
    echo "starting deliver"
    env.slave_instance_id = slave_instance_id
    sh "sudo bash deliver_slave.sh"
    echo "ending deliver"
}

echo "finishing Jenkinsfile"
