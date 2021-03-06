# This file is part of HamsiManager.
#
# Copyright (c) 2010 - 2015 Murat Demir <mopened@gmail.com>
#
# Hamsi Manager is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# Hamsi Manager is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with HamsiManager; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA


from FileUtils import Musics
import FileUtils as fu
import os
from Core.MyObjects import *
from Core import Dialogs
from Core import Organizer
import time
from Core import Universals as uni
from Core import ReportBug


class MusicPlayer(MWidget):
    def __init__(self, _parent, _type="bar", _file=""):
        MWidget.__init__(self, _parent)
        self.Player = None
        self.PlayerName = None
        self.info = None
        self.file = _file
        self.type = _type
        self.tbPause = MToolButton(self)
        self.tbPause.setToolTip(translate("Player", "Pause / Continue"))
        self.tbPause.setIcon(MIcon("Images:mediaPause.png"))
        self.tbPause.setAutoRaise(True)
        self.tbPause.setCheckable(True)
        self.tbMute = MToolButton(self)
        self.tbMute.setToolTip(translate("Player", "Mute"))
        self.tbMute.setIcon(MIcon("Images:playerMute.png"))
        self.tbMute.setAutoRaise(True)
        self.tbMute.setCheckable(True)
        self.tbPlay = MToolButton(self)
        self.tbPlay.setToolTip(translate("Player", "Play"))
        self.tbPlay.setIcon(MIcon("Images:mediaPlay.png"))
        self.tbPlay.setAutoRaise(True)
        self.tbStop = MToolButton(self)
        self.tbStop.setToolTip(translate("Player", "Stop"))
        self.tbStop.setIcon(MIcon("Images:mediaStop.png"))
        self.tbStop.setAutoRaise(True)
        self.tbPause.setEnabled(False)
        self.tbMute.setEnabled(False)
        self.tbStop.setEnabled(False)
        MObject.connect(self.tbPause, SIGNAL("clicked()"), self.pause)
        MObject.connect(self.tbMute, SIGNAL("clicked()"), self.mute)
        MObject.connect(self.tbPlay, SIGNAL("clicked()"), self.play)
        MObject.connect(self.tbStop, SIGNAL("clicked()"), self.stop)
        if _type == "bar":
            #little style for bar
            HBOXs = []
            HBOXs.append(MHBoxLayout())
            HBOXs[0].addWidget(self.tbPause)
            HBOXs[0].addWidget(self.tbPlay)
            HBOXs[0].addWidget(self.tbStop)
            HBOXs[0].addWidget(self.tbMute)
            HBOXs.append(MHBoxLayout())
            self.tbPause.setMaximumHeight(16)
            self.tbMute.setMaximumHeight(16)
            self.tbPlay.setMaximumHeight(16)
            self.tbStop.setMaximumHeight(16)
            VBOX = MVBoxLayout()
            VBOX.setSpacing(0)
            VBOX.addLayout(HBOXs[1])
            VBOX.addLayout(HBOXs[0])
            self.setLayout(VBOX)
            self.setMaximumSize(150, 40)
        elif _type == "dialog":
            #full style for dialog
            self.info = MLabel(
                translate("Player", "Please Select The File You Want To Play And Click The Play Button."))
            HBOXs = []
            HBOXs.append(MHBoxLayout())
            HBOXs[0].addWidget(self.tbPause)
            HBOXs[0].addWidget(self.tbPlay)
            HBOXs[0].addWidget(self.tbStop)
            HBOXs[0].addWidget(self.tbMute)
            HBOXs.append(MHBoxLayout())
            HBOXs[1].addWidget(self.info)
            VBOX = MVBoxLayout()
            VBOX.setSpacing(0)
            VBOX.addLayout(HBOXs[1])
            VBOX.addLayout(HBOXs[0])
            self.setLayout(VBOX)
            MApplication.processEvents()
            self.info.setMinimumWidth(len(self.info.text()) * 7)
            self.tbPause.setMinimumHeight(22)
            self.tbMute.setMinimumHeight(22)
            self.tbPlay.setMinimumHeight(22)
            self.tbStop.setMinimumHeight(22)
            self.setMaximumSize(390, 44)
            self.infoScroller = InfoScroller(self)
            self.infoScroller.start()

    def setInfoText(self, _info):
        if self.type == "bar":
            getMainWindow().StatusBar.showMessage(_info)
        else:
            MApplication.processEvents()
            if self.info is not None:
                self.info.setText(_info)
                self.info.setMinimumWidth(len(self.info.text()) * 7)

    def play(self, _filePath="", _isPlayNow=True):
        try:
            MApplication.processEvents()
            playerName = uni.MySettings["playerName"]
            if self.Player is None or self.PlayerName != playerName:
                self.stop()
                self.PlayerName = playerName
                if playerName == "Phonon":
                    self.Player = M_Phonon()
                elif playerName == "Phonon (PySide)":
                    self.Player = M_Phonon_PySide()
                elif playerName == "tkSnack":
                    self.Player = M_tkSnack()
                else:
                    self.Player = M_MPlayer()
            self.stop()
            if _filePath == "":
                _filePath = getMainTable().values[getMainTable().currentRow()]["path"]
            if _filePath == "" and self.file != "":
                _filePath = self.file
            else:
                self.file = _filePath
            _filePath = fu.checkSource(_filePath, "file")
            if _filePath is not None:
                import Taggers

                if Taggers.getTagger(True) is not None:
                    self.musicTags = Musics.readMusicFile(_filePath, False)
                    self.setInfoText(str(("%s - %s (%s)") % (
                        self.musicTags["artist"], self.musicTags["title"], self.musicTags["album"])))
                else:
                    self.musicTags = None
                    self.setInfoText(str("- - -"))
                if _isPlayNow:
                    if self.Player.play(_filePath):
                        self.tbPause.setEnabled(True)
                        self.tbMute.setEnabled(True)
                        self.tbStop.setEnabled(True)
                        self.tbPlay.setEnabled(False)
        except:
            ReportBug.ReportBug()

    def stop(self):
        try:
            try: self.Player.stop()
            except: pass
            self.tbPlay.setEnabled(True)
            self.tbPause.setEnabled(False)
            self.tbMute.setEnabled(False)
            self.tbPause.setChecked(False)
            self.tbMute.setChecked(False)
            self.tbStop.setEnabled(False)
            if self.type == "bar":
                self.setInfoText(
                    translate("Player", "Please Select The File You Want To Play And Click The Play Button."))
        except:
            ReportBug.ReportBug()

    def mute(self):
        try:
            self.Player.mute()
        except:
            ReportBug.ReportBug()

    def pause(self):
        try:
            self.Player.pause()
        except:
            ReportBug.ReportBug()

    def runTo(self):
        try:
            second = 0  #TODO: add slider or something
            self.Player.runTo(second)
        except:
            ReportBug.ReportBug()

    def seek(self, _state):
        try:
            self.Player.seek(_state)
        except:
            ReportBug.ReportBug()


class M_Phonon():
    def __init__(self):
        self.m_media = None
        self.paused = False
        self.muted = False

    def play(self, _filePath):
        if self.m_media is not None:
            self.stop()
        try:
            from PyQt4.phonon import Phonon
        except:
            Dialogs.showError(translate("Player", "Phonon Is Not Installed On Your System."),
                              translate("Player",
                                        "We could not find the Phonon(PyQt4) module installed on your system.<br>Please choose another player from the options or <br>check your Phonon installation."))
            return False
        if not self.m_media:
            self.m_media = Phonon.MediaObject(getMainWindow())
            self.audioOutput = Phonon.AudioOutput(Phonon.MusicCategory, getMainWindow())
            Phonon.createPath(self.m_media, self.audioOutput)
        self.m_media.setCurrentSource(
            Phonon.MediaSource(str(_filePath)))
        self.m_media.play()
        self.paused = False
        return True

    def pause(self):
        if self.paused:
            self.m_media.play()
            self.paused = False
        else:
            self.m_media.pause()
            self.paused = True

    def stop(self):
        if self.m_media is not None:
            self.m_media.stop()
        self.paused = False

    def runTo(self, _second):
        self.m_media.seek(_second)

    def seek(self, _state):
        pass

    def mute(self):
        if self.muted:
            self.audioOutput.setMuted(False)
            self.muted = False
        else:
            self.audioOutput.setMuted(True)
            self.muted = True


class M_Phonon_PySide():
    def __init__(self):
        self.m_media = None
        self.paused = False
        self.muted = False

    def play(self, _filePath):
        if self.m_media is not None:
            self.stop()
        try:
            from PySide.phonon import Phonon
        except:
            Dialogs.showError(translate("Player", "Phonon Is Not Installed On Your System."),
                              translate("Player",
                                        "We could not find the Phonon(PySide) module installed on your system.<br>Please choose another player from the options or <br>check your Phonon installation."))
            return False
        if not self.m_media:
            self.m_media = Phonon.MediaObject()
            self.audioOutput = Phonon.AudioOutput(Phonon.MusicCategory)
            Phonon.createPath(self.m_media, self.audioOutput)
        self.m_media.setCurrentSource(Phonon.MediaSource(str(_filePath)))
        self.m_media.play()
        self.paused = False
        return True

    def pause(self):
        if self.paused:
            self.m_media.play()
            self.paused = False
        else:
            self.m_media.pause()
            self.paused = True

    def stop(self):
        if self.m_media is not None:
            self.m_media.stop()
        self.paused = False

    def runTo(self, _second):
        self.m_media.seek(_second)

    def seek(self, _state):
        pass

    def mute(self):
        if self.muted:
            self.audioOutput.setMuted(False)
            self.muted = False
        else:
            self.audioOutput.setMuted(True)
            self.muted = True


class M_tkSnack():
    def __init__(self):
        self.tada = None

    def play(self, _filePath):
        if self.tada is not None:
            self.stop()
        from Tkinter import Tk
        import tkSnack

        self.root = Tk()
        tkSnack.initializeSnack(self.root)
        self.tada = tkSnack.Sound(file=_filePath)
        self.tada.play()
        return True

    def pause(self):
        self.tada.pause()

    def stop(self):
        if self.tada is not None:
            self.tada.stop()

    def runTo(self, _second):
        pass

    def seek(self, _state):
        pass

    def mute(self):
        pass


class M_MPlayer():
    def __init__(self):
        self.popen = False

    def runCommand(self, _command):
        if self.popen is not False:
            from Core.Execute import writeToPopen

            writeToPopen(self.popen, _command)

    def play(self, _filePath):
        from Core import Execute

        if self.popen is not False:
            self.runCommand("quit")
        command = [uni.MySettings["mplayerPath"]]
        command += uni.MySettings["mplayerArgs"].split(" ")
        command += [uni.MySettings["mplayerAudioDevicePointer"],
                    uni.MySettings["mplayerAudioDevice"],
                    str(_filePath)]
        self.popen = Execute.execute(command)
        return True

    def pause(self):
        self.runCommand("pause")

    def stop(self):
        self.runCommand("quit")
        try: self.popen.close()
        except: pass
        self.popen = False

    def runTo(self, _second):
        self.runCommand("seek " + str(_second))

    def seek(self, _state):
        self.runCommand("seek " + str(_state) + " 100")

    def mute(self):
        self.runCommand("mute")


class InfoScroller(MThread):
    def __init__(self, _parent):
        MThread.__init__(self)
        self.parent = _parent

    def run(self):
        if self.parent.info is not None:
            x = 150
            breakCount = 0
            while 1 == 1:
                try:
                    if uni.isStartingSuccessfully and uni.isStartedCloseProcess is False:
                        if self.parent.parent().isVisible():
                            try:
                                self.parent.info.move(x, 0)
                                time.sleep(0.05)
                                x -= 1
                                self.parent.info.setMinimumWidth(len(self.parent.info.text()) * 7)
                                if x <= -(len(self.parent.info.text()) * 7):
                                    x = 150
                            except: pass  # Passed for cleared objects
                        else:
                            breakCount += 1
                            if breakCount < 5: time.sleep(1)
                            else: break
                    else:
                        breakCount += 1
                        if breakCount < 5: time.sleep(1)
                        else: break
                except:  # Passed for cleared objects or starting or stoping
                    breakCount += 1
                    if breakCount < 5: time.sleep(1)
                    else: break
                
    
