import copy
import os
from os.path import dirname, realpath
import json
import subprocess
import sys
import yaml

from utils import get_reqs

PATH_TO_CURRENT_DIRECTORY = dirname(realpath(__file__))

python_requirements = get_reqs("../requirements.txt")
system_requirements = get_reqs("../system_requirements.md")
print("system_requirements:", system_requirements)

# create build steps
for partial_file_name in ["1-install-dependencies", "3-load-places"]:
    with open("templates/" + partial_file_name + ".template.sh") as f1:
        with open("build_steps/" + partial_file_name + ".sh", "w") as f2:
            template = f1.read()
            output = template.replace("{{system_reqs}}", " ".join(system_requirements))
            output = output.replace("{{python_reqs}}", " ".join(python_requirements))
            f2.write(output)

run_packer_text = """
# https://www.packer.io/intro/getting-started/build-image.html
# https://www.packer.io/docs/builders/amazon.html#iam-task-or-instance-role

echo "validating packer.json"
packer validate packer.json

packer build -var "aws_access_key=$AWS_ACCESS_KEY_ID" -var "aws_secret_key=$AWS_SECRET_ACCESS_KEY" -var "aws_owner_id=$AWS_OWNER_ID" packer.json
"""

with open("templates/packer.template.yaml") as f:
    text = f.read()

template = yaml.load(text)

## create first packer.json with just dependencies installed

configs = [
    {
        "builders.0.source_ami_filter.owners": ["099720109477"],
        "builders.0.ami_name": "firstdraftgis-base",
        "provisioners": [
            {"type": "shell", "script": "../build_steps/1-install-dependencies.sh"},
            {"type": "shell", "script": "../build_steps/2-install-mapnik.sh"}
        ],
        "builders.0.source_ami_filter.filters.name": "ubuntu/images/*ubuntu-xenial-16.04-amd64-server-*"
    },
    {
        "builders.0.source_ami_filter.owners": ["{{user `aws_owner_id`}}"],
        "builders.0.ami_name": "firstdraftgis-loaded",
        "provisioners": [
            {"type": "shell", "script": "../build_steps/3-load-places.sh"},
        ],
        "builders.0.source_ami_filter.filters.name": "firstdraftgis-base"        
    },
    {
        "builders.0.source_ami_filter.owners": ["{{user `aws_owner_id`}}"],
        "builders.0.ami_name": "firstdraftgis-exported",
        "provisioners": [
            {"type": "shell", "script": "../build_steps/4-conform-training-data.sh"},
        ],
        "builders.0.source_ami_filter.filters.name": "firstdraftgis-loaded"         
    }
]

for index, config in enumerate(configs):
    packer_obj = copy.copy(template)
    for key, value in config.items():
        obj = packer_obj
        subkeys = key.split(".")
        print("subkeys:", subkeys)
        num_subkeys = len(subkeys)
        for subkey in subkeys[:-1]:
            if subkey.isdigit():
                obj = obj[int(subkey)]
            else:
                obj = obj[subkey]
        obj[subkeys[-1]] = value
    filepath = "packer" + str(index) + ".json"        
    with open("built/" + filepath, "w") as f:
        print("packer_obj:", type(packer_obj))
        json.dump(packer_obj, f, indent=4)
        print("dumped")
        
    print("path:", "built/" + filepath)
    subprocess.call(["packer", "validate", filepath], cwd="built")
    print("packer tried to validate")
    
    with open("built/packer" + str(index) + ".sh", "w") as f:
        f.write(run_packer_text.replace("packer.json", "packer" + str(index) + ".json"))



