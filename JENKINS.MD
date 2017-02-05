#How to set up Jenkins

- Install Jenkins Server
- Install ec2-plugin
- Connect to the Jenkins Server
    - run ```sudo visudo```
    - add the following to the bottom:
    ```
    jenkins ALL= NOPASSWD: ALL
    tomcat ALL= NOPASSWD: ALL
    ```
