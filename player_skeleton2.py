 #----------------------------------------------------------------------
# player_skeleton2.py
#
# Created: 04/15/2010
#
# Author: Mike Driscoll - mike@pythonlibrary.org
#----------------------------------------------------------------------

import os
import wx
import wx.media
import random
import wx.lib.buttons as buttons
from command_handler import *

dirName = os.path.dirname(os.path.abspath(__file__))
bitmapDir = os.path.join(dirName, 'bitmaps')

########################################################################
class MediaPanel(wx.Panel):
    """"""

    #----------------------------------------------------------------------
    def __init__(self, parent):
        """Constructor"""
        wx.Panel.__init__(self, parent=parent)
        
        self.frame = parent
        self.currentVolume = 50
        self.createMenu()
        self.layoutControls()
        
        sp = wx.StandardPaths.Get()
        self.currentFolder = sp.GetDocumentsDir()
        self.current_song = 0
        self.file_list = []

        self.timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.onTimer)
        self.timer.Start(100)

        # Running voice recognition
        self.commandHandler = CommandHandlerThread(self)

        self.Bind(wx.EVT_CHAR_HOOK, self.onKeyPress)

        self.Bind(V_EVT_PLAY, self.onVoicePlay)
        self.Bind(V_EVT_PAUSE, self.onVoicePause)
        self.Bind(V_EVT_STOP, self.onVoiceStop)
        self.Bind(V_EVT_NEXT, self.onVoiceNext)
        self.Bind(V_EVT_PREV, self.onVoicePrev)
        self.Bind(V_EVT_RND_OFF, self.onVoiceRandomOff)
        self.Bind(V_EVT_RND_ON, self.onVoiceRandomOn)
        self.Bind(V_EVT_RPT_OFF, self.onVoiceRepeatOff)
        self.Bind(V_EVT_RPT_ON, self.onVoiceRepeatOn)
        self.Bind(V_EVT_VOL, self.onVoiceVolumeChange)

    #----------------------------------------------------------------------
    def layoutControls(self):
        """
        Create and layout the widgets
        """
        
        try:
            self.mediaPlayer = wx.media.MediaCtrl(self, style=wx.SIMPLE_BORDER)
        except NotImplementedError:
            self.Destroy()
            raise

        # create song label
        self.songLabel = wx.StaticText(self, style=wx.ALIGN_CENTER)

        # create playback slider
        self.playbackSlider = wx.Slider(self, size=wx.DefaultSize)
        self.Bind(wx.EVT_SLIDER, self.onSeek, self.playbackSlider)
        
        self.volumeCtrl = wx.Slider(self, style=wx.SL_VERTICAL|wx.SL_INVERSE)
        self.volumeCtrl.SetRange(0, 100)
        self.volumeCtrl.SetValue(self.currentVolume)
        self.volumeCtrl.Bind(wx.EVT_SLIDER, self.onSetVolume)
                
        # Create sizers
        mainSizer = wx.BoxSizer(wx.VERTICAL)
        hSizer = wx.BoxSizer(wx.HORIZONTAL)
        audioSizer = self.buildAudioBar()
                
        # layout widgets
        mainSizer.Add(self.songLabel, 1, wx.ALL|wx.EXPAND, 5)
        mainSizer.Add(self.playbackSlider, 1, wx.ALL|wx.EXPAND, 5)
        hSizer.Add(audioSizer, 0, wx.LEFT|wx.CENTER, 5)
        hSizer.Add(self.volumeCtrl, 0, wx.RIGHT, 5)
        mainSizer.Add(hSizer)
        
        self.SetSizer(mainSizer)
        self.Layout()
        
    #----------------------------------------------------------------------
    def buildAudioBar(self):
        """
        Builds the audio bar controls
        """
        audioBarSizer = wx.BoxSizer(wx.HORIZONTAL)
        
        self.buildBtn({'bitmap':'player_prev.png', 'handler':self.onPrev,
                       'name':'prev'},
                      audioBarSizer)

        img = wx.Bitmap(os.path.join(bitmapDir, "player_random.png"))
        self.randomBtn = buttons.GenBitmapToggleButton(self, bitmap=img, name="random")
        self.randomBtn.Enable(True)

        img = wx.Bitmap(os.path.join(bitmapDir, "player_random.png"))
        self.randomBtn.SetBitmapSelected(img)
        self.randomBtn.SetInitialSize()

        self.randomBtn.Bind(wx.EVT_BUTTON, self.onRandomOn)
        audioBarSizer.Add(self.randomBtn, 0, wx.LEFT, 2)

        img = wx.Bitmap(os.path.join(bitmapDir, "player_repeat.png"))
        self.repeatBtn = buttons.GenBitmapToggleButton(self, bitmap=img, name="repeat")
        self.repeatBtn.Enable(True)

        img = wx.Bitmap(os.path.join(bitmapDir, "player_repeat.png"))
        self.repeatBtn.SetBitmapSelected(img)
        self.repeatBtn.SetInitialSize()
        audioBarSizer.Add(self.repeatBtn, 0, wx.LEFT, 2)
        
        # create play/pause toggle button
        img = wx.Bitmap(os.path.join(bitmapDir, "player_play.png"))
        self.playPauseBtn = buttons.GenBitmapToggleButton(self, bitmap=img, name="play")
        self.playPauseBtn.Enable(False)

        img = wx.Bitmap(os.path.join(bitmapDir, "player_pause.png"))
        self.playPauseBtn.SetBitmapSelected(img)
        self.playPauseBtn.SetInitialSize()
        
        self.playPauseBtn.Bind(wx.EVT_BUTTON, self.onPlay)
        audioBarSizer.Add(self.playPauseBtn, 0, wx.LEFT, 3)
        
        btnData = [{'bitmap':'player_stop.png',
                    'handler':self.onStop, 'name':'stop'},
                    {'bitmap':'player_next.png',
                     'handler':self.onNext, 'name':'next'}]
        for btn in btnData:
            self.buildBtn(btn, audioBarSizer)
            
        return audioBarSizer
                    
    #----------------------------------------------------------------------
    def buildBtn(self, btnDict, sizer):
        """"""
        bmp = btnDict['bitmap']
        handler = btnDict['handler']
                
        img = wx.Bitmap(os.path.join(bitmapDir, bmp))
        btn = buttons.GenBitmapButton(self, bitmap=img, name=btnDict['name'])
        btn.SetInitialSize()
        btn.Bind(wx.EVT_BUTTON, handler)
        sizer.Add(btn, 0, wx.LEFT, 3)
        
    #----------------------------------------------------------------------
    def createMenu(self):
        """
        Creates a menu
        """
        menubar = wx.MenuBar()
        
        fileMenu = wx.Menu()
        open_file_menu_item = fileMenu.Append(wx.NewId(), "&Open", "Open a File")
        menubar.Append(fileMenu, '&File')
        self.frame.SetMenuBar(menubar)
        self.frame.Bind(wx.EVT_MENU, self.onBrowse, open_file_menu_item)
        
    #----------------------------------------------------------------------
    def loadMusic(self, musicFile):
        """"""
        if not self.mediaPlayer.Load(musicFile):
            wx.MessageBox("Unable to load %s: Unsupported format?" % musicFile,
                          "ERROR",
                          wx.ICON_ERROR | wx.OK)
        else:
            self.mediaPlayer.SetInitialSize()
            self.GetSizer().Layout()
            self.playbackSlider.SetRange(0, self.mediaPlayer.Length())
    
    #----------------------------------------------------------------------
    def onBrowse(self, event):
        """
        Opens file dialog to browse for music folder
        """

        ddg = wx.DirDialog(
            self, message="Choose a folder in which you have your music stored", defaultPath=self.currentFolder,
            style=wx.DD_DEFAULT_STYLE | wx.DD_DIR_MUST_EXIST
         )

        if ddg.ShowModal() == wx.ID_OK:
            self.currentFolder = ddg.GetPath()
            for fname in os.listdir(self.currentFolder):  # os.listdir returns the list of files in the currentFolder given in brackets
                if fname.endswith('.mp3') or fname.endswith('.wav'):
                    self.file_list.append(fname)
                self.loadMusic(os.path.join(self.currentFolder, self.file_list[self.current_song]))
            self.playPauseBtn.Enable(True)
            if self.file_list[0].endswith('.mp3') or self.file_list[0].endswith('.wav'):
                self.songLabel.SetLabelText(self.file_list[0][:-4])
                self.GetSizer().Layout()

        ddg.Destroy()

    #----------------------------------------------------------------------
    def onNext(self, event):
        """
        Switch to the next song in a folder (needs to be manually restarted)
        """
        if not self.repeatBtn.GetValue():
            self.current_song = self.current_song + 1
            if self.current_song >= len(self.file_list):
                self.current_song = 0

        self.mediaPlayer.Stop()
        self.playPauseBtn.SetToggle(False)

        if not self.mediaPlayer.Load(os.path.join(self.currentFolder, self.file_list[self.current_song])):
            wx.MessageBox("Unable to load %s: Unsupported format?"
                          % os.path.join(self.currentFolder, self.file_list[self.current_song]),
                          "ERROR",
                          wx.ICON_ERROR | wx.OK)
        elif self.file_list[self.current_song].endswith('.mp3') or self.file_list[self.current_song].endswith('.wav'):
                self.songLabel.SetLabelText(self.file_list[self.current_song][:-4])
                self.GetSizer().Layout()

    #----------------------------------------------------------------------
    def onPause(self):
        """
        Pauses the music
        """
        self.mediaPlayer.Pause()
    
    #----------------------------------------------------------------------
    def onPlay(self, event):
        """
        Plays the music
        """
        if not event.GetIsDown():
            self.onPause()
            return
        
        if not self.mediaPlayer.Play():
            wx.MessageBox("Unable to Play media : Unsupported format?",
                          "ERROR",
                          wx.ICON_ERROR | wx.OK)
        else:
            self.mediaPlayer.SetInitialSize()
            self.GetSizer().Layout()
            self.playbackSlider.SetRange(0, self.mediaPlayer.Length())
            if self.playbackSlider.Position == self.mediaPlayer.Length():
                self.current_song = self.current_song + 1

    #----------------------------------------------------------------------
    def onPrev(self, event):
        """
        Switch to previous song in a folder (needs to be manually restarted)
        """
        if not self.repeatBtn.GetValue():
            self.current_song = self.current_song - 1
            if self.current_song < 0:
                self.current_song = len(self.file_list) - 1

        self.mediaPlayer.Stop()
        self.playPauseBtn.SetToggle(False)

        if not self.mediaPlayer.Load(os.path.join(self.currentFolder, self.file_list[self.current_song])):
            wx.MessageBox("Unable to load %s: Unsupported format?"
                          % os.path.join(self.currentFolder, self.file_list[self.current_song]),
                          "ERROR",
                          wx.ICON_ERROR | wx.OK)
        elif self.file_list[self.current_song].endswith('.mp3') or self.file_list[self.current_song].endswith('.wav'):
                self.songLabel.SetLabelText(self.file_list[self.current_song][:-4])
                self.GetSizer().Layout()

    #----------------------------------------------------------------------
    def onRandomOff(self):
        """
        Sorts the playlist
        """
        self.file_list = sorted(self.file_list)

    #----------------------------------------------------------------------
    def onRandomOn(self, event):
        """
        Shuffles the playlist.
        """

        if not event.GetIsDown():
            self.onRandomOff()
            return

        random.shuffle(self.file_list)

    #----------------------------------------------------------------------
    def onSeek(self, event):
        """
        Seeks the media file according to the amount the slider has
        been adjusted.
        """
        offset = self.playbackSlider.GetValue()
        self.mediaPlayer.Seek(offset)
        
    #----------------------------------------------------------------------
    def onSetVolume(self, event):
        """
        Sets the volume of the music player
        """
        self.currentVolume = self.volumeCtrl.GetValue()
        self.mediaPlayer.SetVolume(self.currentVolume / 100)
    
    #----------------------------------------------------------------------
    def onStop(self, event):
        """
        Stops the music and resets the play button
        """
        self.mediaPlayer.Stop()
        self.playPauseBtn.SetToggle(False)
        
    #----------------------------------------------------------------------
    def onTimer(self, event):
        """
        Keeps the player slider updated
        """
        offset = self.mediaPlayer.Tell()
        self.playbackSlider.SetValue(offset)

    #----------------------Voice controll handlers-------------------------
    def onKeyPress(self, event):
        """
        Run voice recognition when spacebar is pressed
        """
        keycode = event.GetKeyCode()
        if keycode == wx.WXK_SPACE:
            self.commandHandler.recognize()

        event.Skip()

    #----------------------------------------------------------------------
    def onVoicePlay(self, event):
        """
        Play the song when command is received
        """
        if not self.mediaPlayer.Play():
            wx.MessageBox("Unable to Play media : Unsupported format?",
                          "ERROR",
                          wx.ICON_ERROR | wx.OK)
        else:
            self.mediaPlayer.SetInitialSize()
            self.GetSizer().Layout()
            self.playbackSlider.SetRange(0, self.mediaPlayer.Length())
            self.playPauseBtn.SetToggle(True)

    #----------------------------------------------------------------------
    def onVoicePause(self, event):
        """
        Pause current song when command is received
        """
        self.mediaPlayer.Pause()
        self.playPauseBtn.SetToggle(False)

    #----------------------------------------------------------------------
    def onVoiceRandomOff(self, event):
        """
        Sorts the playlist when command is received
        """
        if self.randomBtn.GetValue():
            self.file_list = sorted(self.file_list)
            self.randomBtn.SetValue(False)

    #----------------------------------------------------------------------
    def onVoiceRandomOn(self, event):
        """
        Sorts the playlist when command is received
        """
        if not self.randomBtn.GetValue():
            random.shuffle(self.file_list)
            self.randomBtn.SetValue(True)

    #----------------------------------------------------------------------
    def onVoiceRepeatOff(self, event):
        """
        Sorts the playlist when command is received
        """

        self.repeatBtn.SetValue(False)

    #----------------------------------------------------------------------
    def onVoiceRepeatOn(self, event):
        """
        Sorts the playlist when command is received
        """

        self.repeatBtn.SetValue(True)

    #----------------------------------------------------------------------
    def onVoiceStop(self, event):
        """
        Stop current song when command is received
        """
        self.mediaPlayer.Stop()
        self.playPauseBtn.SetToggle(False)

    #----------------------------------------------------------------------
    def onVoiceNext(self, event):
        """
        Switch to the next song in a folder when command is received (needs to be manually restarted)
        """
        self.current_song = self.current_song + 1
        if self.current_song >= len(self.file_list):
            self.current_song = 0

        self.mediaPlayer.Stop()
        self.playPauseBtn.SetToggle(False)

        if not self.mediaPlayer.Load(os.path.join(self.currentFolder, self.file_list[self.current_song])):
            wx.MessageBox("Unable to load %s: Unsupported format?"
                          % os.path.join(self.currentFolder, self.file_list[self.current_song]),
                          "ERROR",
                          wx.ICON_ERROR | wx.OK)
        elif self.file_list[self.current_song].endswith('.mp3') or self.file_list[self.current_song].endswith('.wav'):
                self.songLabel.SetLabelText(self.file_list[self.current_song][:-4])
                self.GetSizer().Layout()

    # ----------------------------------------------------------------------
    def onVoicePrev(self, event):
        """
        Switch to previous song in a folder when command is received (needs to be manually restarted)
        """
        self.current_song = self.current_song - 1
        if self.current_song < 0:
            self.current_song = len(self.file_list) - 1

        self.mediaPlayer.Stop()
        self.playPauseBtn.SetToggle(False)

        if not self.mediaPlayer.Load(os.path.join(self.currentFolder, self.file_list[self.current_song])):
            wx.MessageBox("Unable to load %s: Unsupported format?"
                          % os.path.join(self.currentFolder, self.file_list[self.current_song]),
                          "ERROR",
                          wx.ICON_ERROR | wx.OK)
        elif self.file_list[self.current_song].endswith('.mp3') or self.file_list[self.current_song].endswith('.wav'):
                self.songLabel.SetLabelText(self.file_list[self.current_song][:-4])
                self.GetSizer().Layout()

    #----------------------------------------------------------------------
    def onVoiceVolumeChange(self, event):
        self.currentVolume += event.change
        if self.currentVolume > 100:
            self.currentVolume = 100
        elif self.currentVolume < 0:
            self.currentVolume = 0
        self.mediaPlayer.SetVolume(self.currentVolume / 100)
        self.volumeCtrl.SetValue(self.currentVolume)

########################################################################
class MediaFrame(wx.Frame):
 
    #----------------------------------------------------------------------
    def __init__(self):
        wx.Frame.__init__(self, None, wx.ID_ANY, "Python Music Player")
        panel = MediaPanel(self)
        
#----------------------------------------------------------------------
# Run the program
if __name__ == "__main__":
    app = wx.App(False)
    frame = MediaFrame()
    frame.Show()
    app.MainLoop()
