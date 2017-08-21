from __future__ import print_function
import pprint
import time
from kivy.uix.widget import Widget
from kivy.properties import NumericProperty, ObjectProperty, StringProperty, \
                            BooleanProperty, DictProperty, ListProperty


def flatten_json(json):
    if type(json) == dict:
        for k, v in list(json.items()):
            if type(v) == dict:
                flatten_json(v)
                json.pop(k)
                for k2, v2 in v.items():
                    json[k+"_"+k2] = v2
    return json


class ActualData(object):
    channel_channelid = StringProperty('')
    channel_channelname = StringProperty('')
    channel_channelnumber = NumericProperty(0)
    channel_provider = StringProperty('?')

    present_channelid = StringProperty('?')
    present_components = ListProperty([])
    present_description = StringProperty('?')
    present_duration = NumericProperty(0)
    present_endtime = NumericProperty(0)
    present_eventid = NumericProperty(0)
    present_hastimer = BooleanProperty(0)
    present_isrunning = BooleanProperty(0)
    present_parentalrating = NumericProperty(0)
    present_runningstatus = NumericProperty(0)
    present_seen = NumericProperty(0)
    present_shorttext = StringProperty('?')
    present_starttime = NumericProperty(0)
    present_timermatch = StringProperty('?')
    present_title = StringProperty('?')
    present_vps = BooleanProperty(0)

    following_channelid = StringProperty('?')
    following_components = ListProperty([])
    following_description = StringProperty('?')
    following_duration = NumericProperty(0)
    following_endtime = NumericProperty(0)
    following_eventid = NumericProperty(0)
    following_hastimer = NumericProperty(0)
    following_isrunning = BooleanProperty(0)
    following_parentalrating = NumericProperty(0)
    following_runningstatus = NumericProperty(0)
    following_seen = NumericProperty(0)
    following_shorttext = StringProperty('?')
    following_starttime = NumericProperty(0)
    following_timermatch = StringProperty('?')
    following_title = StringProperty('?')
    following_vps = NumericProperty(0)

    streaminfo_dolbidigital = BooleanProperty(False)
    streaminfo_encrypted = BooleanProperty(False)
    streaminfo_multilang = NumericProperty(0)
    streaminfo_radio = BooleanProperty(False)
    streaminfo_videoheight = NumericProperty(0)
    streaminfo_videowidth = NumericProperty(0)
    streaminfo_vtx = BooleanProperty(False)

    epg_progress_max = NumericProperty(0)
    epg_progress_value = NumericProperty(0)

    def update_actual(self, data):
        for key, value in data.iteritems():
            setattr(self, key, value)

        now = int(time.time()) # seconds since epoch
        self.epg_progress_max = self.present_duration #  self.present_endtime - self.present_starttime
        self.epg_progress_value = now - self.present_starttime


class ReplayData(object):
    replay_active = BooleanProperty(False)
    replay_basename = StringProperty('?')
    replay_event_components = ListProperty([])
    replay_event_description = StringProperty('')
    replay_event_duration = NumericProperty(0)
    replay_event_endtime = NumericProperty(0)
    replay_event_eventid = NumericProperty(0)
    replay_event_hastimer = BooleanProperty(False)
    replay_event_isrunning = BooleanProperty(False)
    replay_event_parentalrating = NumericProperty(0)
    replay_event_runningstatus = NumericProperty(0)
    replay_event_seen = NumericProperty(0)
    replay_event_shorttext = StringProperty('')
    replay_event_starttime = NumericProperty(0)
    replay_event_timermatch = BooleanProperty(False)
    replay_event_title = StringProperty('?')
    replay_event_vps = BooleanProperty(False)
    replay_filename = StringProperty('')
    replay_filesizemb = NumericProperty(0)
    replay_folder = StringProperty('')
    replay_hasmarks = BooleanProperty(False)
    replay_images = ListProperty([])
    replay_info_aux = StringProperty('')
    replay_info_channelid = StringProperty('')
    replay_info_channelname = StringProperty('')
    replay_info_description = StringProperty('')
    replay_info_framespersecond = NumericProperty(0)
    replay_isedited = BooleanProperty(False)
    replay_isnew = BooleanProperty(False)
    replay_lengthinseconds = NumericProperty(0)
    replay_name = StringProperty('?')
    replay_start = NumericProperty(0)
    replay_title = StringProperty('?')

    def update_replay(self, data):
        for key, value in data.items():
            k = 'replay_' + key
            if not hasattr(self, k):
                print("new value!", k)
            setattr(self, k, value)


class ReplayControlData(object):
    replaycontrol_active = BooleanProperty(False)
    replaycontrol_play = BooleanProperty(0)
    replaycontrol_current = NumericProperty(0)
    replaycontrol_forward = BooleanProperty(0)
    replaycontrol_active = BooleanProperty(0)
    replaycontrol_total = NumericProperty(1606)
    # replaycontrol_speed values:
    # -1: playing, 1-3 fast forward/backward (use replaycontrol_forward)
    replaycontrol_speed = NumericProperty(-1)

    def update_replaycontrol(self, data):
        for key, value in data.items():
            k = 'replaycontrol_' + key
            setattr(self, k, value)
        if self.replaycontrol_active and self.sm.current not in ('replay', 'remote', 'menu'):
            self.sm.current = 'replay'
            print("current screen:", self.sm.current)
        elif not self.replaycontrol_active and self.sm.current == 'replay':
            self.sm.current = 'livetv'


class TimerData(object):
    is_recording = BooleanProperty(False)
    timers = ListProperty([])

    def update_timers(self, data):
        #print([timer for timer in data])
        self.timers = sorted([
            {'time_text': time.strftime("%H:%M", time.localtime(timer.get('starttime'))),
             'date_text': time.strftime("%d.%m.%y", time.localtime(timer.get('starttime'))),
             'title_text':  timer.get('event_title'),
             'duration_text': "%d'" % (int(timer.get('event_duration') / 60)),
             'channel_text': timer.get('channel_channelname'),
             'is_recording': timer.get('recording'),
             'starttime': timer.get('starttime'),
        } for timer in data], key=lambda k: k['starttime'])
        self.is_recording = any(bool(timer.get('recording', False))
                                for timer in data)


class RecordingsData(object):
    recordings = ListProperty([])

    def update_recordings(self, data):
        #TODO update recordig info
        #print([rec for rec in data])
        self.recordings = sorted([
            {'time_text': time.strftime("%H:%M", time.localtime(recording.get('event_starttime'))),
             'date_text': time.strftime("%d.%m.%y", time.localtime(recording.get('event_starttime'))),
             'title_text': recording.get('event_title'),
             'duration_text': "%d'" % (int(recording.get('event_duration') / 60)),
             'starttime': recording.get('event_starttime'),
             'is_recording': recording.get('event_hastimer'),
            } for recording in data], key=lambda k: k['starttime'], reverse=True)


class CustomData(object):
    customdata = DictProperty({})

    def update_customdata(self, data):
        for key, value in data.items():
            k = 'custom_' + key
            if not hasattr(self, k):
                print("new key", k, "with value", value)
            setattr(self.customdata, k, value)


class RolechangeData(object):
    rolechange = DictProperty({})
    rolechange_havelogos = BooleanProperty()

    def update_rolechange(self, data):
        self.rolechange_havelogos = bool(data.get('havelogos'))
        for key, value in data.items():
            k = 'rolechange_' + key
            if not hasattr(self, k):
                print("new key", k, "with value", value)
            setattr(self.customdata, k, value)


class SkinstateData(object):
    skin_attached = BooleanProperty()
    skin_attached = False

    def update_skinstate(self, data):
        self.skin_attached = bool(data.get('attached', 0))

        #if self.skin_attached is True and self.sm.current != 'menu':
        #    self.last_screen = self.sm.current
        #    self.sm.current = 'menu'
        #elif self.skin_attached is False:
        #    self.sm.current = self.last_screen


class ButtonsData(object):
    btn_red = StringProperty("")
    btn_green = StringProperty("")
    btn_yellow = StringProperty("")
    btn_blue = StringProperty("")
    def update_buttons(self, data):
        for btn in ('red', 'green', 'yellow', 'blue'):
            setattr(self, 'btn_' + btn, data.get(btn, ''))

# TODO:
# data for menu
class MenuData(object):
    menu_list = ListProperty([])
    menu_data = {}
    menu_title = StringProperty('')
    menu_category = NumericProperty(0)
    menu_editable = BooleanProperty(False)
    osd_message = StringProperty('')
    menu_lines = NumericProperty(15)

    def update_menu(self, data):
        for key, value in data.items():
            k = 'menu_' + key
            if not hasattr(self, k):
                print("new key", k, "with value", value)
            setattr(self, k, value)

    def update_menuitem(self, data):
        #TODO Menu categories (like recordings need additional layout options
        #print(data)
        self.menu_data[data['index']] = data
        self.menu_list = sorted([
            {'text': item['text'].replace('\t', '  '),
             'id': 'menu_item_' + str(item['index']),
             'selected': item['current'],
             'selectable': item['selectable'],
             'index': item['index'],
             } for item in self.menu_data.values()], key=lambda k: k['index'])
        #print(self.menu_list)

    def update_message(self, data):
        self.osd_message = data['message']

    def update_scrollbar(self, data):
        pass
        #print("Menu scolling:", data)

    def clearmenu(self, data):
        self.menu_list = []
        self.menu_data = {}
        self.menu_title = ''
        self.menu_category = 0
        self.menu_editable = False

    def activate_menu_entry(self, index, selected):
        if not selected:
            try:
                sel_index = next((item['index'] for item in self.menu_list if item['selected']))
            except StopIteration:
                return
            delta = index - sel_index
            if delta < 0:
                self.send_key('Up', abs(delta))
            else:
                self.send_key('Down', delta)
        else:
            self.send_key('Ok')


# data for scrollbar


class osd2webData(
        ActualData, ReplayData, ReplayControlData, TimerData, RecordingsData,
        CustomData, RolechangeData, SkinstateData, ButtonsData, MenuData):
    pass
