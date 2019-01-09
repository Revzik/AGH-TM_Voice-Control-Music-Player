from threading import Thread
import wx

class CommandHandlerThread(Thread):

    def __init__(self, notify_window):
        pass

    def execute(self, command):
        if command == 'play':
            self.play()
        elif command == 'pause':
            self.pause()
        elif command == 'stop':
            self.stop()
        elif command == 'volumeUp':
            self.volumeUp()
        elif command == 'volumeDown':
            self.volumeDown()

    def play(self):
        pass

    def pause(self):
        print("Paused")
        pass

    def stop(self):
        pass

    def next(self):
        pass

    def prev(self):
        pass

    def volumeUp(self):
        volumeOffset = 10

    def volumeDown(self):
        volumeOffset = -10