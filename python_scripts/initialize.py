from django.utils.crypto import get_random_string
from os.path import dirname
from os.path import join
from os.path import realpath

SECRET_KEY = get_random_string()

directory_of_this_file = dirname(realpath(__file__))

filepath = join(directory_of_this_file, "../projfd/projfd/additional_settings/secrets.py")
print("filepath:", filepath)

with open(filepath, "w") as f:
    f.write("SECRET_KEY = '" + SECRET_KEY + "'")
