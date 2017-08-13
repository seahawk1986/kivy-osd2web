from __future__ import print_function
import time
from datetime import timedelta, datetime
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
    channel_channelid = StringProperty('?')
    channel_channelname = StringProperty('Carpe Diem')
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
    time_delta = 0

    def update_actual(self, data):
        for key, value in data.iteritems():
            setattr(self, key, value)
            if key.startswith('present_'):
                print(key, value)

        self.time_delta = self.present_seen - int(time.time())
        print("seconds delta to epg clock:", self.time_delta)
        self.epg_progress_max = self.present_endtime - self.present_starttime
        self.epg_progress_value = self.present_seen - self.present_starttime


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
            #print(k, value)


class ReplayControlData(object):
    replaycontrol_active = BooleanProperty(False)
    replaycontrol_play = BooleanProperty(0)
    replaycontrol_current = NumericProperty(0)
    replaycontrol_forward = BooleanProperty(0)
    replaycontrol_active = BooleanProperty(1)
    replaycontrol_total = NumericProperty(1606)
    # replaycontrol_speed values:
    # -1: playing, 1-3 fast forward/backward (use replaycontrol_forward)
    replaycontrol_speed = NumericProperty(-1)

    def update_replaycontrol(self, data):
        for key, value in data.items():
            k = 'replaycontrol_' + key
            print(k, value)
            setattr(self, k, value)

class TimerData(object):
    is_recording = BooleanProperty(False)
    timer = ListProperty([])

    def update_timer(self, data):
        #TODO update timer list
        print(data)
        self.timer = [flatten_json(timer) for timer in data]
        self.is_recording = any(bool(timer['event']['isrunning']) for timer in self.data.get('timers', []))
        print(self.timer)


class RecordingsData(object):
    recordings = ListProperty([])
    def update_recordings(self, data):
        #TODO update recordig info
        self.recordings = [flatten_json(recording) for recording in data]
        print(self.recordings)

# TODO:
# data for rolechange:
# data for skinstate:
# data for customdata:
class osd2webData(
        ActualData, ReplayData, ReplayControlData, TimerData, RecordingsData,
        ):
    pass
