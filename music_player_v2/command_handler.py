class CommandHandler:

    def __init__(self, panel):
        self.panel_ = panel

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
        self.panel_.onPlay()

    def pause(self):
        self.panel_.onPause()

    def stop(self):
        self.panel_.onStop()

    def volumeUp(self):
        self.panel_.currentVolume += 10
        if self.panel_.currentVolume > 100:
            self.panel_.currentVolume = 100

    def volumeDown(self):
        self.panel_.currentVolume -= 10
        if self.panel_.currentVolume < 0:
            self.panel_.currentVolume = 0
