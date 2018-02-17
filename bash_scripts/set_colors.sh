# from https://stackoverflow.com/questions/20909942/color-the-linux-command-output

# has to be run manually in the terminal shell
norm="$(printf '\033[0m')" #returns to "normal"
bold="$(printf '\033[0;1m')" #set bold
red="$(printf '\033[0;31m')" #set red
green="$(printf '\033[0;32m')" #set green
boldred="$(printf '\033[0;1;31m')" #set bold, and set red.
boldgreen="$(printf '\033[0;1;32m')" #set bold, and set red.


# used to run docker build .  | sed -e "s/Step .*/\n\n${boldgreen}&${norm}/g"