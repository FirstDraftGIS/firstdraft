#How to set up Jenkins

###Install Jenkins Server
###Install ec2-plugin
###Add Init Script
Add the following to the init script for the ec2-plugin found under Configure System:
```
export JAVA="/usr/bin/java";
sudo apt-get update;
sudo apt-get install -y default-jre;
sudo apt-get install -y default-jdk;
```

### Update Permissions
Run it once through. It'll fail because find method in the jenkinsfiles isn't approved.  We need this in order to get the instance to save.  Here's the url to the scripts page on the main Jenkins Instance
http://jenkins.firstdraftgis.com/jenkins/scriptApproval/

Here's the script signatures that you'll have to approve:
```
staticMethod org.codehaus.groovy.runtime.DefaultGroovyMethods find java.lang.String java.lang.String
```

### Install AWSCLI
Install AWS Command Line Interface, which is used by save to execute aws command
```
sudo apt-get install awscli
```

### Configure AWS
We have to first log in as the tomcat user because that user runs Jenkins
```
sudo su tomcat
sudo aws configure
```

You may have to run the following depending on your setup.
- Connect to the Jenkins Server
    - run ```sudo visudo```
    - add the following to the bottom:
    ```
    jenkins ALL= NOPASSWD: ALL
    tomcat ALL= NOPASSWD: ALL
    ```
