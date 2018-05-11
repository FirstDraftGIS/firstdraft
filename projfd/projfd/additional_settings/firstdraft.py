from os.path import join
from os.path import expanduser


# manually set this because otherwise if use home directory, will try to use
# /var/www/
#USER_HOME_DIRECTORY = "/home/usrfd/"
#MAPS_DIRECTORY = join("/tmp", "maps")
MAPS_DIRECTORY = "/tmp/maps"

# used for geojson.io output
PUBLIC_BASE_URL = "http://52.23.197.49"