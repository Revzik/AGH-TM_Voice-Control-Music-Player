from threading import Thread
import wx
from wx.lib.newevent import NewEvent
from ..voicecontrol.run_sarmata import runSarmata

EventVPlay, V_EVT_PLAY = NewEvent()
EventVPause, V_EVT_PAUSE = NewEvent()
EventVStop, V_EVT_STOP = NewEvent()
EventVNext, V_EVT_NEXT = NewEvent()
EventVPrev, V_EVT_PREV = NewEvent()
EventVVolUp, V_EVT_VOL_UP = NewEvent()
EventVVolDn, V_EVT_VOL_DN = NewEvent()


class CommandHandlerThread(Thread):

    def __init__(self, notify_window):
        Thread.__init__(self)
        self.notify_window = notify_window
        self.start()

    def recognize(self):
        self.execute(runSarmata())

    def execute(self, command):
        if command == 'play':
            self.play()
        elif command == 'pause':
            self.pause()
        elif command == 'stop':
            self.stop()
        elif command == 'next':
            self.next()
        elif command == 'prev':
            self.prev()
        elif command == 'volumeUp':
            self.volumeUp()
        elif command == 'volumeDown':
            self.volumeDown()

    def play(self):
        wx.PostEvent(self.notify_window, EventVPlay())

    def pause(self):
        wx.PostEvent(self.notify_window, EventVPause())

    def stop(self):
        wx.PostEvent(self.notify_window, EventVStop())

    def next(self):
        wx.PostEvent(self.notify_window, EventVNext())

    def prev(self):
        wx.PostEvent(self.notify_window, EventVPrev())

    def volumeUp(self):
        offset = 10
        wx.PostEvent(self.notify_window, EventVVolUp(change=offset))

    def volumeDown(self):
        offset = -10
        wx.PostEvent(self.notify_window, EventVVolDn(change=offset))