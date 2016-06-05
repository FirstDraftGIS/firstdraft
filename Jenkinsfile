import com.amazonaws.auth.AWSCredentials
import com.amazonaws.auth.PropertiesCredentials
import com.amazonaws.services.ec2.AmazonEC2Client

echo "starting Jenkinsfile"

// some code from http://docs.aws.amazon.com/AWSSdkDocsJava/latest/DeveloperGuide/tutorial-spot-instances-java.html
AWSCredentials credentials = null
credentials = PropertiesCredentials(GettingStartedApp.class.getResourceAsStream("AwsCredentials.properties"))
AmazonEC2 ec2 = AmazonEC2Client(credentials)


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
    
    sh "aws ec2 terminate-instances --dry-run --instance-ids " + slave_instance_id
    
    echo "ending deliver"
}

echo "finishing Jenkinsfile"
