# kivy-osd2web
proof of concept for a kivy application that communicates with the osd2web plugin for VDR

# Dependencies
 - python2.7
 - twisted
 - kivy 1.10.0
 - autobahn

# configuration
By default the app tries to connec to localhost on port 4444.
Creating a `vdrstatusapp.ini` configuration file in the app directory allows to set a custom host (or ip) and port:

```ini
[connection]
host = yavdr07
port = 4444
```
