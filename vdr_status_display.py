#!/usr/bin/env python2
# -*- coding: utf-8 -*-
from __future__ import print_function
from kivy.support import install_twisted_reactor
install_twisted_reactor()
import json
import locale
import pprint
import sys
import time
from kivy.app import App
from kivy.clock import Clock
from kivy.config import Config
from kivy.lang.builder import Builder
from kivy.properties import NumericProperty, ObjectProperty, DictProperty
from kivy.properties import StringProperty, BooleanProperty, ListProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from twisted.python import log
from twisted.internet import reactor
from twisted.internet.protocol import ReconnectingClientFactory
from autobahn.twisted.websocket import WebSocketClientFactory, \
                                       WebSocketClientProtocol, \
                                       connectWS
from datamodel import VDRData
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
         print("Binary message received: {0} bytes".format(len(payload)))
      else:
         data = json.loads(payload.decode('utf-8'))
         self.factory.app.vdr.parse_data(data)

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


#####
locale.setlocale(locale.LC_ALL, '')
Config.set('graphics', 'fullscreen', 'auto')
#Config.set('graphics', 'window_state', 'maximized')
Builder.load_file('VDRstatus.kv')


class BlockLabel(Label):
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
    channelname = StringProperty("unknown")
    localtime = ObjectProperty(time.localtime())
    date = StringProperty()
    is_replay_active = BooleanProperty(False)
    is_playing = BooleanProperty(False)
    is_recording = BooleanProperty(False)
    epg_title = StringProperty("Connecting to VDR...")
    current_title = StringProperty("...")
    current_starttime = ObjectProperty(time.localtime())
    current_endtime = ObjectProperty(time.localtime())
    progress_max = NumericProperty(1000)
    progress_value = NumericProperty(0)

    def __init__(self, **kwargs):
        super(MyLayout, self).__init__(**kwargs)
        Clock.schedule_interval(self.update_vars, 1)

    def update_vars(self, *args):
        self.localtime = time.localtime()
        current_starttime = app.vdr.current.starttime
        current_endtime = app.vdr.current.endtime
        self.current_starttime = time.localtime(int(current_starttime))
        self.current_endtime = time.localtime(int(current_endtime))
        duration = current_endtime - current_starttime
        progress_in_s = int(time.time()) - current_starttime
        try:
            self.progress_value = (
                    float(progress_in_s) / float(duration) * 1000.0)
        except ZeroDivisionError:
            self.progress_value = 0
        self.is_replay_active = app.vdr.is_replay_active
        self.is_playing = bool(app.vdr.replaycontrol.play)
        self.is_recording = any(bool(timer['event']['isrunning']) for timer in app.vdr.timers)
        if self.is_replay_active:
            self.current_title = app.vdr.replay.event['title']
            self.channelname = app.vdr.replay.info['channelname']
        else:
            self.current_title = app.vdr.current.title
            self.channelname = app.vdr.channel.channelname


class VDRStatusAPP(App):
    def build(self):
        self.vdr = VDRData()
        layout = MyLayout()
        self.vdr.update = layout.update_vars
        log.startLogging(sys.stdout)
        pp = pprint.PrettyPrinter(indent=4)
        factory = MyClientFactory(self, url="ws://yavdr07:4444", protocols=['osd2vdr'])
        #reactor.connectTCP('ws://yavdr07', 4444, MyClientFactory(self), protocols=['osd2vdr'], )
        connectWS(factory)
        return layout

if __name__ == '__main__':
    app = VDRStatusAPP()
    app.run()
