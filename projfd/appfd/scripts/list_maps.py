from os import listdir
from os.path import isdir, isfile

def run():
    for filename in listdir("/home/usrfd/maps"):
        print "/home/usrfd/maps/" + filename
        if isdir("/home/usrfd/maps/" + filename):
            for part in listdir("/home/usrfd/maps/" + filename):
                print "\tpart = ", part
       
