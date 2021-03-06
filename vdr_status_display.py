#!/usr/bin/env python2
# -*- coding: utf-8 -*-
from __future__ import print_function
from collections import OrderedDict
from functools import partial
from kivy.support import install_twisted_reactor
install_twisted_reactor()
import argparse
import ast
from datetime import datetime, timedelta
import json
import locale
import mimetypes
import pprint
import sys
import time
from functools import partial
from kivy.app import App
from kivy.clock import Clock
from kivy.config import Config
from kivy.properties import NumericProperty, ObjectProperty, StringProperty, \
                            BooleanProperty, DictProperty, ListProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.image import AsyncImage
from kivy.uix.label import Label
from kivy.uix.recycleview import RecycleView
from kivy.uix.recycleboxlayout import RecycleBoxLayout
from kivy.uix.spinner import Spinner
from kivy.uix.behaviors.focus import FocusBehavior
from kivy.uix.recycleview.layout import LayoutSelectionBehavior

from twisted.internet import reactor
from twisted.python import log
from autobahn.twisted.websocket import connectWS

from osd2web_data import osd2webData, flatten_json
from screens import MyScreenManager, MenuScreen, LiveTVScreen, ReplayScreen, \
                    TimerScreen, RecordingsScreen, ClockScreen
from websocket import WSClientFactory
from webcontrol import WebControllerFactory

mimetypes.guess_extension = partial(mimetypes.guess_extension, strict=False)

#class AsyncImage(AsyncImage):
#    pass


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

class SelectableRecycleBoxLayout(FocusBehavior, LayoutSelectionBehavior,
                                  RecycleBoxLayout):
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


class VDRStatusAPP(App, osd2webData):
    pretty_printer = pprint.PrettyPrinter(indent=4)
    url = StringProperty('localhost:4444')
    screens = OrderedDict([
        (LiveTVScreen, 'livetv'),
        (ReplayScreen, 'replay'),
        (TimerScreen, 'timers'),
        (RecordingsScreen, 'recordings'),
        (MenuScreen, 'menu'),
        (ClockScreen, 'clock'),
    ])

    channelname = StringProperty("Welcome to yaVDR")
    localtime = ObjectProperty(time.localtime())
    now = StringProperty("00:00")
    date = StringProperty("Carpe diem.")
    datetime = StringProperty("day, dd:mm:YY 00:00")
    rec_color_active = ListProperty([1, .1, .1, 1])
    rec_color_inactive = ListProperty([.3, .3, .3, .7])
    last_screen = 'livetv'
    connection = None
    is_startup = True

    def __init__(self, **kwargs):
        self.pp = self.pretty_printer.pprint
        self.update_register = {
            'actual': self.update_actual,
            'customdata': self.update_customdata,
            'recordings': self.update_recordings,
            'replay': self.update_replay,
            'replaycontrol': self.update_replaycontrol,
            'rolechange': self.update_rolechange,
            'skinstate': self.update_skinstate,
            'timers': self.update_timers,
            'buttons': self.update_buttons,
            'menu': self.update_menu,
            'menuitem': self.update_menuitem,
            'clearmenu': self.clearmenu,
            'message': self.update_message,
            'scrollbar': self.update_scrollbar,
        }

        super(VDRStatusAPP, self).__init__(**kwargs)
        Clock.schedule_interval(self.update_clock, 1)

    def change_screen(self, screen, popup=None):
        """change the screen, optinally destroy popup if given"""
        if self.sm.current != screen:
            self.sm.current = screen
        if popup is not None:
            popup.dismiss()

    def send_menu_lenght(self, lines=None):
        if lines is None:
            lines = self.menu_lines
        if self.connection is not None:
            category_list = []
            for i in range(29):
                category_list.append({"category": i,"maxlines": lines,"shape": 1})
            self.connection.factory.protocol.broadcast_message(
                    {"event":"maxlines",
                     "object": {"categories": category_list}
                     })

    def toggle_client_active(self):
        if not self.skin_attached:
            self.takefocus()
        else:
            self.leavefocus()

    def takefocus(self):
        if not self.skin_attached:
            self.connection.factory.protocol.broadcast_message(
                {"event":"takefocus"}
            )

    def leavefocus(self):
        self.connection.factory.protocol.broadcast_message(
            {"event":"leavefocus"}
        )


    def send_key(self, key, repeat=1):
        """send a keypress with a given number of repeats"""
        if self.connection is not None:
            if key == 'Menu':
                self.takefocus()
                self.send_menu_lenght()
            self.connection.factory.protocol.broadcast_message(
                {
                    'event': 'keypress',
                    'object': {
                        'key': key,
                        'repeat': repeat,
                    }
                })

    def update_data(self, name, data):
        # TODO: move to update_* functions if really needed
        if isinstance(data, dict):
            data = flatten_json(data)
        elif isinstance(data, list):
            flattened_items = []
            for item in data:
                if isinstance(item, dict):
                    item = flatten_json(item)
                flattened_items.append(item)
            data = flattened_items
        #print("debug show raw data:")
        #self.pp(data)
        update_function = self.update_register.get(name, None)
        if update_function is None:
            print("unhandled event:", name)
            self.pp(data)
        else:
            update_function(data)

    def get_chan_img(self):
        channel_url_template = u"http://%s:%s/data/channellogo?name=%s&id=%s"
        if (app.rolechange_havelogos and app.channel_channelname and app.current != 'replay'):
            return channel_url_template % (\
                app.config.get('connection', 'host'), app.config.get('connection', 'port'),\
                quote(app.channel_channelname.encode('utf-8')), app.channel_channelid)\

        else:
            return 'icons/menu.png'

    def update_clock(self, *args):
        self.localtime = time.localtime()
        now = datetime.now()
        self.date = now.strftime("%A, %d. %B %Y")
        self.now = now.strftime("%H:%M")
        self.datetime = now.strftime("%a, %d.%m.%y %H:%M")
        if self.replaycontrol_active and self.replaycontrol_play:
            self.replaycontrol_current += 1
        self.epg_progress_value = int(time.time()) - self.present_starttime

    def handle_webctrl_message(self, msg):
        data = msg.split()
        command, args = data[0], data[1:]

        if command == 'screen':

            try:
                if args:
                    screen = args[0]
                    if screen in self.screens.values():
                        self.sm.current = screen
                        response = 250, ["Ok"]
                    else:
                        raise ValueError('invalid screen name')
                else:
                    raise ValueError('no screen name given')
            except ValueError as e:
                screens = " ".join(self.screens.values())
                response = 501, [
                        str(e),
                        "possible screen names are: {}".format(screens),
                        ]
        else:
            response = 500, ["unknown command"]
        return response

    def build_config(self, config):
        config.setdefaults('connection',
            {
                'host': 'localhost',
                'port': 4444,
            })
        config.setdefaults('TCPControl',
            {
                'port': 8877,
                'enabled': True,
            })
        config.setdefaults('skin',
            {
                'default_screen': 'livetv',
                'rec_color_active': [1, 0.1, 0.1, 1],
                'rec_color_inactive': [0.3, 0.3, 0.3, 0.7],
                'menu_lines': 15
            })

    def build(self):
        self.sm = MyScreenManager()
        for screen_class, screen_name in self.screens.iteritems():
            self.sm.add_widget(screen_class(name=screen_name, id=screen_name))
        self.url = "ws://{}:{}".format(self.config.get('connection', 'host'),
                                       self.config.getint('connection', 'port'))

        self.wsfactory = WSClientFactory(self, url=self.url, protocols=['osd2vdr'])
        self.connection = connectWS(self.wsfactory)

        if ast.literal_eval(self.config.get('TCPControl', 'enabled')):
            webctrl_port = self.config.getint('TCPControl', 'port')
            self.webctrlfactory = WebControllerFactory(self)
            reactor.listenTCP(webctrl_port, WebControllerFactory(self))

        self.rec_color_active = ast.literal_eval(
            self.config.get('skin', 'rec_color_active'))
        self.rec_color_inactive = ast.literal_eval(
            self.config.get('skin', 'rec_color_inactive'))
        self.menu_lines = self.config.getint('skin', 'menu_lines')
        self.default_screen = self.config.get('skin', 'default_screen')
        if not self.default_screen in self.screens.values():
            print("WARNING: invalid name for default screen")
        elif self.is_startup:
            self.is_startup = False
            self.sm.current = self.default_screen
            self.sm.last = self.default_screen
        return self.sm

if __name__ == '__main__':
    log.startLogging(sys.stdout)
    locale.setlocale(locale.LC_ALL, '')
    app = VDRStatusAPP()
    try:
        app.run()
    except KeyboardInterrupt:
        app.stop()
