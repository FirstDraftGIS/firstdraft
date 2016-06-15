echo "starting Jenkinsfile"

def agent_name = ""


node('ec2') {
  stage "Build"
  agent_name = env.NODE_NAME
  sh 'wget https://raw.githubusercontent.com/FirstDraftGIS/firstdraft/master/bash_scripts/build.sh -O /tmp/build.sh'
  sh 'sudo bash /tmp/build.sh'

  stage "Test"
  sh 'wget https://raw.githubusercontent.com/FirstDraftGIS/firstdraft/master/bash_scripts/test.sh -O /tmp/test.sh'
  sh 'sudo bash /tmp/test.sh'

  stage "Load"
  sh 'wget https://raw.githubusercontent.com/FirstDraftGIS/firstdraft/master/bash_scripts/load.sh -O /tmp/load.sh'
  sh 'sudo bash /tmp/load.sh'
}
agent_instance_id = agent_name.find(/i\-[a-z\d]+/)

stage "Deliver"
node('master') {
    echo "starting deliver"
    env.agent_instance_id = agent_instance_id
    sh 'wget https://raw.githubusercontent.com/FirstDraftGIS/firstdraft/master/bash_scripts/deliver.sh -O /tmp/deliver.sh'
    sh "bash /tmp/deliver.sh"
    echo "ending deliver"
}

echo "finishing Jenkinsfile"
