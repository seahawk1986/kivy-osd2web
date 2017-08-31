# kivy-osd2web
proof of concept for a kivy application that communicates with the osd2web plugin for VDR

# Dependencies
This app has the following dependencies (the debian/ubuntu Package name is in brackets, Ubuntu >= 16.04 has the needed package versions)
 - python2.7 (kivy's twisted integration does not work with python3)
 - kivy >= 1.10.0 (python-kivy from https://launchpad.net/~kivy-team/+archive/ubuntu/kivy)
 - twisted (python-twisted)
 - autobahn (python-autobahn)
 - RobotoCondensed-Regular.ttf (fonts-roboto)
 
 If your distributions's packages are to old (e.g. on Ubuntu 14.04) or you simply want the newest versions, you can install the python packages with pip in a virtualenv:
 
 ```
sudo apt-get install git python-virtualenv python-dev build-essential fonts-roboto python-pip
sudo apt-get install libsdl2-ttf-dev libsdl2-net-dev libsdl2-mixer-dev
sudo apt-get install libsdl2-gfx-dev libsdl2-dev libsdl2-image-dev
sudo apt-get install python-pygame python-opengl libgl1-mesa-dev libgles2-mesa-dev
sudo apt-get build-dep kivy cython
virtualenv ~/kivy # choose the directory wisely, you cannot move it without breaking the virtualenv
source ~/kivy/bin/activate # this is needed in every new shell session to use the python libraries from the virtualenv
pip install --upgrade pip setup-tools
pip install --upgrade cython
pip install --upgrade git+https://github.com/kivy/kivy.git@master
pip install --upgrade twisted autobahn # this may take a while to complete
 ```

# Configuration
By default the app tries to connect to `localhost` on port `4444`.
You can change the `vdrstatusapp.ini` configuration file in the app directory to set a custom host (or ip) and port in the `[connection]` section:

```ini
[connection]
host = yavdr07
port = 4444

[skin]
default_screen = livetv
menu_lines = 15

[TCPControl]
port = 8877
enabled = True
```
# Running the App

```
./vdr_status_display [--auto-fullscreen]
```

# Changing the screen
kivy-osd2web provides several screens displaying different information sent by osd2web. When replaying a recording it switches to the replay screen (except if you are on the menu screen which also provides remote control buttons). If the replay is stopped, it switches bach to the previous screen.

Clicking on the channel logo (or hamburger menu if osd2web is not configured to display channel logos) opens a popup window for screen selection.

If the TCPControl option is enabled, you can list and switch screens by sending a command over a TCP connection, e.g. using netcat (the example uses the BSD nc variant) or vdr's svdrpsend script:
```
$ nc -q1 192.168.1.140 8877 <<< "screen"
SVDRP kivy-osd2web client; UTF-8
501-no screen name given
501 possible screen names are: livetv replay timers recordings menu clock
221 kivy-osd2web closing connection

$ nc -q 1 localhost 8877 <<< "screen timers"
SVDRP kivy-osd2web client; UTF-8
250 Ok
221 kivy-osd2web closing connection

$ svdrpsend -d localhost -p 8877 screen                                                                   
SVDRP kivy-osd2web client; UTF-8
501-no screen name given
501 possible screen names are: livetv replay timers recordings menu clock
221 kivy-osd2web closing connection

$ svdrpsend -p 8877 screen timers                                                                
SVDRP kivy-osd2web client; UTF-8
250 Ok
221 kivy-osd2web closing connection


```
