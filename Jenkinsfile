echo "starting Jenkinsfile"

def agent_name = ""


node('ec2') {
  stage "Build"
  agent_name = env.NODE_NAME
  sh 'wget https://raw.githubusercontent.com/FirstDraftGIS/firstdraft/master/build_agent.sh -O /tmp/build_agent.sh'
  sh 'sudo bash /tmp/build_agent.sh'

  stage "Test"
  sh 'wget https://raw.githubusercontent.com/FirstDraftGIS/firstdraft/master/test_agent.sh -O /tmp/test_agent.sh'
  sh 'sudo bash /tmp/test_agent.sh'
}
agent_instance_id = agent_name.find(/i\-[a-z\d]+/)

stage "Deliver"
node('master') {
    echo "starting deliver"
    env.agent_instance_id = agent_instance_id
    sh 'wget https://raw.githubusercontent.com/FirstDraftGIS/firstdraft/master/deliver_agent.sh -O /tmp/deliver_agent.sh'
    sh "bash /tmp/deliver_agent.sh"
    echo "ending deliver"
}

echo "finishing Jenkinsfile"
