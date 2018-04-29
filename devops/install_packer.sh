# https://www.packer.io/intro/getting-started/build-image.html
# https://www.packer.io/docs/builders/amazon.html#iam-task-or-instance-role

echo "installing packer"
if [ ! -f /usr/local/bin/packer ]; then
    cd /tmp
        rm -fr packer*
        wget https://releases.hashicorp.com/packer/1.2.2/packer_1.2.2_linux_amd64.zip -O packer_1.2.2_linux_amd64.zip 
        echo "downloaded packer"
        unzip packer_1.2.2_linux_amd64.zip
    sudo cp -fr /tmp/packer /usr/local/bin/packer
fi;