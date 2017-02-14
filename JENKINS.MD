#How to set up Jenkins

- Install Jenkins Server
- Install ec2-plugin
- Add the following to the init script for the ec2-plugin found under Configure System:
```
export JAVA="/usr/bin/java";
sudo apt-get update;
sudo apt-get install -y default-jre;
sudo apt-get install -y default-jdk;
```

Run it once through. It'll fail because find method in the jenkinsfiles isn't approved.  We need this in order to get the instance to save.  Here's the url to the scripts page on the main Jenkins Instance
http://jenkins.firstdraftgis.com/jenkins/scriptApproval/

Here's the script signatures that you'll have to approve:
```
staticMethod org.codehaus.groovy.runtime.DefaultGroovyMethods find java.lang.String java.lang.String
```


You may have to run the following depending on your setup.
- Connect to the Jenkins Server
    - run ```sudo visudo```
    - add the following to the bottom:
    ```
    jenkins ALL= NOPASSWD: ALL
    tomcat ALL= NOPASSWD: ALL
    ```
