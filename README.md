# kivy-osd2web
proof of concept for a kivy application that communicates with the osd2web plugin for VDR

# Dependencies
This app has the following dependencies (the debian/ubuntu Package name is in brackets, Ubuntu >= 16.04 has the needed package versions)
 - python2.7 (kivy's twisted integration does not work with python3)
 - kivy >= 1.10.0 (python-kivy from https://launchpad.net/~kivy-team/+archive/ubuntu/kivy)
 - twisted (python-twisted)
 - autobahn (python-autobahn)
 - RobotoCondensed-Regular.ttf (fonts-roboto)
 
 If your distributions's packages are to old (e.g. on Ubuntu 14.04) you can install the python packages with pip in a virtualenv:
 
 ```
sudo apt-get install python-virtualenv python-pip build-essential fakeroot fonts-roboto
sudo apt-get build-dep cython
sudo apt-get build-dep kivy
virtualenv ~/kivy # choose the directory wisely, you cannot move it without breaking the virtualenv
source ~/kivy/bin/activate  # this is needed in every new shell session to use the python from the virtualenv
pip install --upgrade pip
pip install --upgrade cython
pip install --upgrade kivy autobahn twisted pillow pygame # this may take a while to complete
 ```

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
