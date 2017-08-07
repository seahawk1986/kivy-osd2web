# -*- coding: utf-8 -*-
import numbers

from kivy.properties import NumericProperty, ObjectProperty, DictProperty
from kivy.properties import StringProperty, BooleanProperty, ListProperty

EMPTY_CHANNEL = {'channelid': "", 'channelname': "...", 'channelnumber': 0, 'provider': ""}
EMPTY_EVENT = {'channelid': '', 'components': [], 'description': '',
               'duration': 0, 'endtime': 0, 'eventid': 0,
               'hastimer': 0, 'isrunning': 0, 'parentalrating': 0,
               'runningstatus': 0, 'seen': 0, 'shorttext': '',
               'starttime': 0, 'timermatch': 'none', 'title': '',
               'vps': 0}
EMPTY_STREAMINFO = {'dolbidigital': 0, 'encrypted': 0, 'multilang': 0, 'radio': 0,
                   'videoheight': 0, 'videowidth': 0, 'vtx': 0}
EMPTY_TIMER = {
    u'event':
        {u'eventid': 40742, u'hastimer': 1, u'isrunning': 0,
         u'parentalrating': 0, u'vps': 1502128800,
         u'title': u'Tagesschau', u'components': [
             {u'type': 1, u'language': u'deu', u'stream': 3, u'description': u''}
             ],
         u'shorttext': u'', u'channelid': u'T-8468-12547-993',
         u'timermatch': u'full', u'starttime': 1502128800,
         u'duration': 900, u'seen': 1502106336,
         u'endtime': 1502129700, u'runningstatus': 0,
         u'description': u'Die Nachrichten der ARD\nProduziert in HD'},
    u'remote': u'', u'starttime': 1502128680, u'firstday': 0,
    u'weekdays': 0, u'day': 1502056800, u'recording': 0,
    u'stoptime': 1502130300, u'flags': 1,
    u'channel': {
        u'channelid': u'T-8468-12547-993', u'channelname': u'SWR BW HD', u'channelnumber': 12, u'provider': u'BR'},
    u'file': u'Tagesschau', u'aux': u'', u'invpsmargin': 0,
    u'expired': 0, u'id': 1, u'pending': 0}
EMPTY_RECORDING = {'basename': '', 'event': {}, 'filename': '',
                   'filesizemb': 0, 'folder': '', 'hasmarks': 0,
                   'images': [],
                   'info': {'channelid': '',
                            'channelname': '',
                            'framespersecond': 0},
                   'isedited': 0, 'isnew': 0, 'lengthinseconds': 0,
                   'name': '', 'start': 0, 'title': ''}
EMPTY_RECORDING_EVENT = {
        'components': [{'description': '', 'language': '', 'stream': 0, 'type': 0},],
        'duration': 0, 'endtime': 0, 'eventid': 0,
        'hastimer': 0, 'isrunning': 0, 'parentalrating': 0,
        'runningstatus': 0, 'seen': 0, 'shorttext': '',
        'starttime': 0, 'timermatch': 'none', 'title': '', 'vps': 0}
EMPTY_REPLAY = {u'info': {u'framespersecond': 50, u'channelid': u'T-8468-16481-16961', u'channelname': u'ZDF HD', u'description': u'Wohin steuern die USA? - Die Executive Orders des Donald Trump\nDie NATO-Man\xf6ver in Polen - Muskelspiele gegen\xfcber Putin\nBahnchef Grube schmei\xdft hin - Die Lage der Bahn AG Moderation: Marietta Slomka\nHD-Produktion', u'aux': u''}, u'isnew': 0, u'name': u'heute-journal', u'filesizemb': 647, u'title': u'30.01.17 22:23  heute-journal', u'basename': u'heute-journal', u'lengthinseconds': 1976, u'filename': u'/srv/vdr/video/heute-journal/2017-01-30.22.23.16-0.rec', u'start': 1485811380, u'hasmarks': 0, u'images': [], u'isedited': 0, u'active': 1, u'folder': u'', u'event': {u'eventid': 20420, u'hastimer': 0, u'isrunning': 0, u'parentalrating': 0, u'vps': 1485811500, u'title': u'heute-journal', u'components': [{u'type': 3, u'language': u'deu', u'stream': 2, u'description': u'Stereo'}, {u'type': 3, u'language': u'mul', u'stream': 2, u'description': u'ohne Originalton'}, {u'type': 3, u'language': u'mis', u'stream': 2, u'description': u'ohne Audiodeskription'}, {u'type': 3, u'language': u'deu', u'stream': 2, u'description': u'Dolby Digital 2.0'}, {u'type': 11, u'language': u'deu', u'stream': 5, u'description': u'HDTV'}, {u'type': 16, u'language': u'deu', u'stream': 3, u'description': u'DVB-Untertitel'}, {u'type': 5, u'language': u'deu', u'stream': 2, u'description': u''}], u'shorttext': u'Wetter', u'timermatch': u'none', u'starttime': 1485811500, u'duration': 1800, u'seen': 1502094450, u'endtime': 1485813300, u'runningstatus': 0, u'description': u'Wohin steuern die USA? - Die Executive Orders des Donald Trump\nDie NATO-Man\xf6ver in Polen - Muskelspiele gegen\xfcber Putin\nBahnchef Grube schmei\xdft hin - Die Lage der Bahn AG Moderation: Marietta Slomka\nHD-Produktion'}}
EMPTY_REPLAY_CONTROL ={u'play': 0, u'current': 0, u'forward': 1, u'active': 0, u'total': 0, u'speed': 0}

class Autofill:
    template = {}
    def __init__(self):
        self.update()

    def update(self, data=None):
        print(data)
        if not data:
            data = self.template
        for key, value in data.items():
            setattr(self, key, value)

class Channel(Autofill):
    template = EMPTY_CHANNEL

class Event(Autofill):
    template = EMPTY_EVENT

class StreamInfo(Autofill):
    template = EMPTY_STREAMINFO

class Replay(Autofill):
    template = EMPTY_REPLAY

class ReplayControl(Autofill):
    template = EMPTY_REPLAY_CONTROL

class VDRData(object):
    role = {}
    is_attached = False
    is_replay_active = False
    is_paused = False
    customdata = {}
    timers = []

    def __init__(self):
        self.channel = Channel()
        self.current = Event()
        self.next = Event()
        self.streaminfo = StreamInfo()
        self.replay = Replay()
        self.replaycontrol = ReplayControl()

    def parse_data(self, data):
        event = data['event']
        obj = data['object']
        if event == 'rolechange':
            self.role = obj
        elif event == 'skinstate':
            self.is_attached = obj.get('attached', 0)
        elif event == 'customdata':
            self.customdata = obj
        elif event == 'actual':
            self.channel.update(obj.get('channel'))
            self.current.update(obj.get('present'))
            self.next.update(obj.get('following'))
            self.streaminfo.update(obj.get('streaminfo'))
        elif event == 'timers':
            print("TIMERS:", obj)
            self.timers = obj  # list
        elif event == 'replay':
            self.is_replay_active = bool(obj['active'])  # number
            self.replay.update(obj)
        elif event == 'replaycontrol':
            self.replaycontrol.update(obj)  # number
        elif event == 'recordings':
            self.recording = obj[0]
            self.recording_event = self.recording.get('event', EMPTY_RECORDING_EVENT)
        self.update()
