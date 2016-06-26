pkill -9 Xvfb;
pkill -9 xvfb;
pkill -9 xvfb-run;
pkill -9 restart_xvfb;
xvfb-run firefox --marionette;
