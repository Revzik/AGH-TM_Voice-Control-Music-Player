from threading import Thread
import wx
from wx.lib.newevent import NewEvent
from voicecontrol.run_sarmata import runSarmata

EventVPlay, V_EVT_PLAY = NewEvent()
EventVPause, V_EVT_PAUSE = NewEvent()
EventVStop, V_EVT_STOP = NewEvent()
EventVNext, V_EVT_NEXT = NewEvent()
EventVPrev, V_EVT_PREV = NewEvent()
EventVRandomOff, V_EVT_RND_OFF = NewEvent()
EventVRandomOn, V_EVT_RND_ON = NewEvent()
EventVRepeatOff, V_EVT_RPT_OFF = NewEvent()
EventVRepeatOn, V_EVT_RPT_ON = NewEvent()
EventVVolChange, V_EVT_VOL = NewEvent()
EventVFinish, V_EVT_FINISH = NewEvent()

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
        elif command == 'randomOff':
            self.randomOff()
        elif command == 'randomOn':
            self.randomOn()
        elif command == 'repeatOff':
            self.repeatOff()
        elif command == 'repeatOn':
            self.repeatOn()
        elif command == 'volumeUpSlight':
            self.volumeChange(5)
        elif command == 'volumeDownSlight':
            self.volumeChange(-5)
        elif command == 'volumeUp':
            self.volumeChange(20)
        elif command == 'volumeDown':
            self.volumeChange(-20)
        elif command == 'finish':
            self.finish()

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

    def randomOff(self):
        wx.PostEvent(self.notify_window, EventVRandomOff())

    def randomOn(self):
        wx.PostEvent(self.notify_window, EventVRandomOn())

    def repeatOff(self):
        wx.PostEvent(self.notify_window, EventVRepeatOff())

    def repeatOn(self):
        wx.PostEvent(self.notify_window, EventVRepeatOn())

    def volumeChange(self, offset):
        wx.PostEvent(self.notify_window, EventVVolChange(change=offset))

    def finish(self):
        wx.PostEvent(self.notify_window, EventVFinish())