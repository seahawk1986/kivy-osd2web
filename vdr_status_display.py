#!/usr/bin/env python2
# -*- coding: utf-8 -*-
from __future__ import print_function
from collections import OrderedDict
from kivy.support import install_twisted_reactor
install_twisted_reactor()
import argparse
from datetime import datetime, timedelta
import json
import locale
import pprint
import sys
import time
from kivy.app import App
from kivy.clock import Clock
from kivy.config import Config
from kivy.properties import NumericProperty, ObjectProperty, StringProperty, \
                            BooleanProperty, DictProperty, ListProperty
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.image import AsyncImage
from kivy.uix.label import Label
from kivy.uix.spinner import Spinner
from twisted.python import log
from twisted.internet import reactor
from twisted.internet.protocol import ReconnectingClientFactory
from autobahn.twisted.websocket import WebSocketClientFactory, \
                                       WebSocketClientProtocol, \
                                       connectWS
from osd2web_data import osd2webData, flatten_json


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
         app.update_data(name, dat)

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


class BlockWidget(object):
    """scale font to fill the label"""
    scale_factor = .95
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


class BlockButton(BlockWidget, Button):
    def __init__(self, **kwargs):
        super(BlockButton, self).__init__(**kwargs)
        self.bind(on_text=self.on_texture_size)
        self.on_texture_size()


class BlockLabel(BlockWidget, Label):
    def __init__(self, **kwargs):
        super(BlockLabel, self).__init__(**kwargs)
        self.on_texture_size()


class ScreenChooserSpinner(Spinner):
    def change_screen(self, *args):
        if self.text in self.values and app.sm.current != "Change Screen":
            app.sm.current = self.text
        self.text = 'Change Screen'


class MenuScreen(Screen):
    pass

class LiveTVScreen(Screen):
    pass

class ReplayScreen(Screen):
    pass

class TimerScreen(Screen):
    pass


class ClockScreen(Screen):
    pass


class MyLayout(BoxLayout):
    pass


class MyScreenManager(ScreenManager):
    pass

class StatusBar(BoxLayout):
    pass

class VDRStatusAPP(App, osd2webData):
    pp = pprint.PrettyPrinter(indent=4)
    screens = OrderedDict([
            (ClockScreen, 'clock'),
            (LiveTVScreen, 'livetv'),
            (ReplayScreen, 'replay'),
            (TimerScreen, 'timer'),
            (MenuScreen, 'menu'),
            ])
    channelname = StringProperty("Welcome to yaVDR")
    localtime = ObjectProperty(time.localtime())
    now = ObjectProperty("00:00")
    date = ObjectProperty("Carpe diem.")
    datetime = ObjectProperty("day, dd:mm:YY 00:00")

    def __init__(self, *args, **kwargs):
        super(VDRStatusAPP, self).__init__()
        Clock.schedule_interval(self.update_clock, 1)

    def update_data(self, name, data):
        if isinstance(data, dict):
            data = flatten_json(data)
        elif isinstance(data, list):
            flattened_items = []
            for item in data:
                if isinstance(item, dict):
                    item = flatten_json(item)
                flattened_items.append(item)
            data = flattened_items
        #self.pp.pprint(data)
        # data for rolechange:
        # data for skinstate:
        # data for customdata:
        # data for recordings:

        update_register = {
                'replay': self.update_replay,
                'replaycontrol': self.update_replaycontrol,
                'timer': self.update_timer,
                'recordings': self.update_recordings,
                'actual': self.update_actual,
                }

        update_function = update_register.get(name, None)
        if update_function is None:
            print(name)
            #self.update_vars(data)
            self.pp.pprint(data)
        else:
            update_function(data)

    def update_clock(self, *args):
        self.localtime = time.localtime()
        now = datetime.now()
        self.date = now.strftime("%A, %d. %B %Y")
        self.now = now.strftime("%H:%M")
        self.datetime = now.strftime("%a, %d.%m.%y %H:%M")
        if self.replaycontrol_active and self.replaycontrol_play:
            self.replaycontrol_current += 1
            print(self.replaycontrol_current)
        self.epg_progress_value = int(time.time()) - self.present_starttime + self.time_delta

    def build_config(self, config):
        config.setdefaults('connection', {
            'host': 'localhost',
            'port': 4444
        })

    def build(self):
        self.sm = MyScreenManager()
        for screen_class, screen_name in self.screens.iteritems():
            self.sm.add_widget(screen_class(name=screen_name))
        url = "ws://{}:{}".format(self.config.get('connection', 'host'),
                                  self.config.getint('connection', 'port'))
        factory = MyClientFactory(self, url=url, protocols=['osd2vdr'])
        connectWS(factory)
        return self.sm

if __name__ == '__main__':
    log.startLogging(sys.stdout)
    locale.setlocale(locale.LC_ALL, '')
    app = VDRStatusAPP()
    try:
        app.run()
    except KeyboardInterrupt:
        app.stop()
