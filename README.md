:warning: Much of this is in the process of being rewritten.  It's currently too expensive to host an always running EC2 instance running First Draft Artificial Intelligence.  I'm currently rewriting all of this to use PostgreSQL on AWS and AWS Lambda, which will be **a lot** cheaper and potentially faster.  If you'd like to help in that effort, please email me at daniel.j.dufour@gmail.com.  Thanks and have a nice day

[![Requirements Status](https://requires.io/github/DanielJDufour/firstdraft/requirements.svg?branch=master)](https://requires.io/github/DanielJDufour/firstdraft/requirements/?branch=master)
[![Hex.pm](https://img.shields.io/hexpm/l/plug.svg?maxAge=2592000?style=plastic)]()

# firstdraft
Automatically generate first drafts of maps

# Installation
The quickest way to get First Draft GIS up and running is to launch the First Draft GIS AMI on AWS found here: https://console.aws.amazon.com/ec2/v2/home?region=us-east-1#Images:visibility=public-images;search=First%20Draft%20GIS;sort=name


# Features
| Languages Supported |
| ------------------- |
| Arabic |
| English |
| Spanish|

#### Important Names
| name | thing |
| --------- | --------- |
| firstdraft | git repo |
| projfd | Django project |
| appfd | Django app |
| dbfd | database |
| usrfd | user|


#### Some Python Packages Installed 
| name | use |
| --------- | --------- |
| beautifulsoup4 | web scraping |
| boto | connect with AWS |
| django | framework that runs the site |
| Pillow | used by Django for ImageField |
| psycopg2 | connects the Django site to the database |
| python-social-auth | used so people can login via Facebook, Google and other things |
| Psycopg | a PostgreSQL database adapater for Python |

# System Packages
Here's a link to a table of the operating system packages that are installed: https://github.com/FirstDraftGIS/firstdraft/blob/master/system_requirements.md

####Create Admin User
The following command will prompt you for a username and email address.
Enter ```admin``` as username and enter your email address.
And enter your password twice.
```
python ~/firstdraft/projbkto/manage.py createsuperuser;
```
