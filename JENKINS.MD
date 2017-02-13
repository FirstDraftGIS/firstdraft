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
- Connect to the Jenkins Server
    - run ```sudo visudo```
    - add the following to the bottom:
    ```
    jenkins ALL= NOPASSWD: ALL
    tomcat ALL= NOPASSWD: ALL
    ```
