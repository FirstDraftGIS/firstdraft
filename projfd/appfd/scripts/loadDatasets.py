#load_datasets
from appfd.scripts.load import run as load
print "load:", dir(load)

def run():
    print "starting loadDatasets"

    with open("/home/usrfd/firstdraft/projfd/appfd/scripts/datasets.txt") as f:
        for line in f.read().splitlines():
            if not line.startswith("#") and line:
                try:
                    load(line)
                except Exception as e:
                    print "CAUGHT EXCEPTION trying to load " + line
                    print e

    print "finishing loadDatasets"
