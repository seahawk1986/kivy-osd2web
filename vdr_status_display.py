#!/usr/bin/env python2
# -*- coding: utf-8 -*-
from __future__ import print_function
from kivy.support import install_twisted_reactor
install_twisted_reactor()
import argparse
import json
import locale
import pprint
import sys
import time
from kivy.app import App
from kivy.clock import Clock
from kivy.config import Config
from kivy.lang import Builder
from kivy.properties import NumericProperty, ObjectProperty, StringProperty, \
                            BooleanProperty, DictProperty, ListProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from twisted.python import log
from twisted.internet import reactor
from twisted.internet.protocol import ReconnectingClientFactory
from autobahn.twisted.websocket import WebSocketClientFactory, \
                                       WebSocketClientProtocol, \
                                       connectWS

def flatten_json(json):
    if type(json) == dict:
        for k, v in list(json.items()):
            if type(v) == dict:
                flatten_json(v)
                json.pop(k)
                for k2, v2 in v.items():
                    json[k+"_"+k2] = v2
    return json

### Websocket Client ###
LOGIN = json.dumps(
        {
            'event': 'login',
            'object': {'type': 1}
        }).encode('utf-8')
LOGOUT = json.dumps(
        {
            'event': 'logout',
            'object': {}
        }).encode('utf-8')

class MyClientProtocol(WebSocketClientProtocol):

   def onConnect(self, response):
       print("Server connected: {0}".format(response.peer))
       self.factory.resetDelay()

   def onOpen(self):
       self.sendMessage(LOGIN)

   def onClose(self):
       self.sendMessage(LOGOUT)

   def onMessage(self, payload, isBinary):
      if isBinary:
         #print("Binary message received: {0} bytes".format(len(payload)))
         pass
      else:
         data = json.loads(payload.decode('utf-8'))
         name = data['event']
         dat = data['object']
         if isinstance(dat, dict):
            dat = flatten_json(dat)
         else:
             dat = {name: dat}
         layout.update_data(name, dat)

   def onClose(self, wasClean, code, reason):
       print("connection closed")
       print(wasClean, code, reason)


class MyClientFactory(WebSocketClientFactory, ReconnectingClientFactory):

    protocol = MyClientProtocol

    def __init__(self, app, *args, **kwargs):
        self.app = app
        super(MyClientFactory, self).__init__(*args, **kwargs)

    def clientConnectionLost(self, connector, reason):
        print("connection lost", reason)
        self.retry(connector)

    def clientConnectionFailed(self, connector, reason):
        print("connection failed", reason)
        self.retry(connector)


### End of Websocket Code ###
locale.setlocale(locale.LC_ALL, '')
# Set window to fullscreen or maximized
Config.set('graphics', 'fullscreen', 'auto')
#Config.set('graphics', 'window_state', 'maximized')


class BlockLabel(Label):
    """scale font to fill the label"""
    scale_factor = 1
    factor = dimension = None

    def on_text(self, *args):
        self.on_texture_size(*args)

    def on_texture_size(self, *args):
        try:
            if not self.factor:
                self.factor = [self.font_size / self.texture_size[0],
                               self.font_size / self.texture_size[1]]
            self.font_size0 = self.size[0] * self.scale_factor * self.factor[0]
            self.font_size1 = self.size[1] * self.scale_factor * self.factor[1]
            if self.font_size0 < self.font_size1:
                self.font_size = self.font_size0
            else:
                self.font_size = self.font_size1
        except ZeroDivisionError:
            pass


class MyLayout(BoxLayout):
    data = DictProperty({})
    is_attached = BooleanProperty(False)
    is_replay_active = BooleanProperty(False)
    first_line = StringProperty("Welcome to yaVDR")
    second_line = StringProperty("Connecting to VDR...")
    localtime = ObjectProperty(time.localtime())
    is_replay_active = BooleanProperty(False)
    is_playing = BooleanProperty(False)
    is_recording = BooleanProperty(False)
    current_starttime = ObjectProperty(time.localtime())
    current_endtime = ObjectProperty(time.localtime())
    progress_max = NumericProperty(1000)
    progress_value = NumericProperty(0)
    pp = pprint.PrettyPrinter(indent=4)

    def __init__(self, **kwargs):
        super(MyLayout, self).__init__(**kwargs)
        Clock.schedule_interval(self.update_vars, 1)

    def update_data(self, name, data):
        for k, v in data.items():
            if name == 'replay':
                k = 'replay_' + k
            elif name == 'replaycontrol':
                k = 'replaycontrol_' + k
            #if isinstance(v, (list, dict)):
            #    print('variable', k, ":")
            #    self.pp.pprint(v)
            #else:
            #    print('variable', k, ":", v)
            self.data[k] = v
        self.update_vars()

    def update_vars(self, *args):
        self.localtime = time.localtime()
        self.is_replay_active = bool(self.data.get('replay_active', 0))
        self.is_recording = any(bool(timer['event']['isrunning']) for timer in self.data.get('timers', []))
        if self.is_replay_active:
            self.is_playing = bool(self.data.get('replaycontrol_play', 0))
            self.first_line = self.data.get('replay_event_title', '?')
            self.second_line = self.data.get('replay_event_shorttext', '')
        else:
            current_starttime = self.data.get('present_starttime', int(time.time()))
            current_endtime = self.data.get('present_endtime', int(time.time()))
            duration = current_endtime - current_starttime
            progress_in_s = int(time.time()) - current_starttime
            try:
                self.progress_value = (
                        float(progress_in_s) / float(duration) * 1000.0)
            except ZeroDivisionError:
                self.progress_value = 0
            self.current_starttime = time.localtime(int(current_starttime))
            self.current_endtime = time.localtime(int(current_endtime))
            self.first_line = self.data.get('channel_channelname', '?')
            self.second_line = self.data.get('present_title', '?')



class VDRStatusAPP(App):

    def build(self):
        Builder.load_file('VDRstatus.kv')
        global layout
        layout = MyLayout()
        log.startLogging(sys.stdout)
        factory = MyClientFactory(self, url=url, protocols=['osd2vdr'])
        connectWS(factory)
        return layout

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='a kivy status display for osd2web')
    host = "localhost"
    port = 4444
    url = "ws://{}:{}".format(host, port)
    app = VDRStatusAPP()
    try:
        app.run()
    except KeyboardInterrupt:
        app.stop()
