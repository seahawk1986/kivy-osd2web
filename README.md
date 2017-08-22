# kivy-osd2web
proof of concept for a kivy application that communicates with the osd2web plugin for VDR

# Dependencies
This app has the following dependencies (the debian/ubuntu Package name is in brackets, Ubuntu >= 16.04 has the needed package versions)
 - python2.7 (kivy's twisted integration does not work with python3)
 - kivy >= 1.10.0 (python-kivy from https://launchpad.net/~kivy-team/+archive/ubuntu/kivy)
 - twisted (python-twisted)
 - autobahn (python-autobahn)
 - RobotoCondensed-Regular.ttf (fonts-roboto)

# Configuration
By default the app tries to connect to `localhost` on port `4444`.
Creating a `vdrstatusapp.ini` configuration file in the app directory allows to set a custom host (or ip) and port:

```ini
[connection]
host = yavdr07
port = 4444
```
# Running the App

```
./vdr_status_display [--auto-fullscreen]
```
