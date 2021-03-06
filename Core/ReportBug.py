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


import os
from Core.MyObjects import *
from Core import Universals as uni
from Core import Dialogs
import FileUtils as fu
from Core import Records
from Core import Settings
from Core import Organizer
import Options
import traceback
import logging
from Core.CommandLineOptions import isQuickMake, QuickMakeParameters, myArgvs

isClose = False
bugDialog = None
lastErrorDetails = None

class ReportBug():
    global bugDialog, lastErrorDetails

    def __init__(self, _isOnlyReport=False):
        global bugDialog, lastErrorDetails
        self.pathOfReportFile = None
        realErrorDetails = ""
        if bugDialog is not None:
            self.pathOfReportFile = bugDialog.pathOfReportFile
        if lastErrorDetails is not None:
            realErrorDetails += lastErrorDetails
        errorDetails = "<b>" + str(
            translate("ReportBug", "Note : You can check and delete your personal informations.")) + "</b><br>"
        try: Records.saveAllRecords()
        except: pass
        try: uni.saveSettings()
        except: pass

        if _isOnlyReport is False:
            lastErrorDetailsValues = sys.exc_info()
            uni.isRaisedAnError = True
            cla, error, trbk = lastErrorDetailsValues
            try:
                excArgs = error.__dict__["args"]
            except:
                excArgs = ""
            try:
                tbf = ""
                for x in traceback.format_tb(trbk, 5):
                    tbf += str(x) + "<br>"
            except: tbf = ""
            realErrorDetails += "<p><b><a name='errorDetails'>" + str(
                translate("ReportBug", "Errors : ")) + "</a></b>" + tbf + "</p>"
            realErrorDetails += (
                "<p><b>" + str(translate("ReportBug", "Error Name : ")) + "</b>" + str(cla.__name__) + "<br><b>" +
                str(translate("ReportBug", "Error : ")) + "</b>" + str(error) + "<br><b>" +
                str(translate("ReportBug", "Error arguments : ")) + "</b>" + str(excArgs) + "</p><hr><p><b>" +
                str(translate("ReportBug", "Last Signal Sender (Object Name,Object Text) : ")) + "</b>&quot;")
            try: realErrorDetails += uni.trUnicode(getMainWindow().sender().objectName())
            except: pass
            realErrorDetails += "&quot;,&quot;"
            try: realErrorDetails += uni.trUnicode(getMainWindow().sender().text())
            except: pass
            realErrorDetails += "&quot;"
            realErrorDetails += "</p>"
            realErrorDetails = realErrorDetails.replace("\\n", "<br>").replace("\'", "&#39;")
            lastErrorDetails = realErrorDetails

        errorDetails += "<hr><b>" + str(translate("ReportBug", "Active Dialog`s Titles : ")) + "</b>"
        try: errorDetails += str(getApplication().activeModalWidget().windowTitle()) + ","
        except: pass
        try: errorDetails += str(getApplication().activePopupWidget().windowTitle()) + ","
        except: pass
        try: errorDetails += str(getApplication().activeWindow().windowTitle()) + ","
        except: pass
        errorDetails += "<br>"
        try:
            errorDetails += "<b>" + str(translate("ReportBug", "Application Version : ")) + "</b>"
            errorDetails += str(uni.version) + "<br>"
        except:
            errorDetails += "<br>"
        try:
            errorDetails += "<b>" + str(translate("ReportBug", "Is Starting Successfully : ")) + "</b>"
            errorDetails += str(uni.isStartingSuccessfully) + "<br>"
            errorDetails += "<b>" + str(translate("ReportBug", "Is Quick Make : ")) + "</b>"
            errorDetails += str(isQuickMake) + "<br>"
            errorDetails += "<b>" + str(translate("ReportBug", "Quick Make Parameters : ")) + "</b>"
            errorDetails += str(QuickMakeParameters) + "<br>"
            errorDetails += "<b>" + str(translate("ReportBug", "My Parameters : ")) + "</b>"
            errorDetails += str(myArgvs) + "<br>"
            errorDetails += "<b>FileSystemCharSet : </b>"
            errorDetails += str(fu.defaultFileSystemEncoding) + " / " + str(
                sys.getfilesystemencoding()).lower() + "<br>"
            errorDetails += "<b>SystemCharSet : </b>"
            errorDetails += str(sys.getdefaultencoding().lower()) + "<br>"
            try:
                errorDetails += "<b>OS Name : </b>"
                errorDetails += str(os.name) + "<br>"
            except:
                errorDetails += "<br>"
            try:
                import platform

                errorDetails += "<b>Python Version : </b>"
                errorDetails += str(platform.python_version()) + "<br>"
                errorDetails += "<b>uname : </b>"
                errorDetails += str(platform.uname()) + "<br>"
                try:
                    errorDetails += "<b>Linux Distribution : </b>"
                    errorDetails += str(platform.linux_distribution()) + "<br>"
                except:
                    errorDetails += "<br>"
            except:
                errorDetails += "<br>"
            try:
                errorDetails += "<b>PyQt4 (Qt) Version : </b>"
                errorDetails += str(PYQT_VERSION_STR) + " (" + str(MT_VERSION_STR) + ")<br>"
            except:
                errorDetails += "<br>"
            try:
                from PyKDE4 import kdecore

                errorDetails += "<b>PyKDE4 Version : </b>"
                errorDetails += str(kdecore.versionString()) + "<br>"
            except:
                errorDetails += "<br>"
            settingKeys = list(uni.MySettings.keys())
            settingKeys.sort()
            for keyName in settingKeys:
                if uni.willNotReportSettings.count(keyName) == 0:
                    errorDetails += "<b>" + str(keyName) + " : " + "</b>"
                    errorDetails += str(uni.MySettings[keyName]) + "<br>"
        except: pass
        try:
            errorDetails += "<b>" + str(translate("ReportBug", "Table Type No : ")) + "</b>" + str(
                uni.tableType) + "<br>"
        except: pass
        errorDetails += str(realErrorDetails)
        self.createErrorPage(errorDetails)
        if bugDialog is None:
            bugDialog = ReportBugDialog(errorDetails, self.pathOfReportFile)
        else:
            try:
                bugDialog.teErrorDetails.setHtml(str(errorDetails.replace("<hr>", "")))
            except:
                bugDialog.teErrorDetails.setHtml(translate("ReportBug",
                                                           "I cannot send the error details due to some character errors.<br>To see the details, please click on the \"Show details file\" button."))
                bugDialog.teErrorDetails.setEnabled(False)
            bugDialog.show()

    def createErrorPage(self, _errorDetails):
        _errorDetails = _errorDetails.replace("\"", "&quot;").replace("\'", "&#39;")
        language = "en_GB"
        if "language" in uni.MySettings:
            language = uni.MySettings["language"]
        htmlString = (
                         '<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">' +
                         '<html xmlns="http://www.w3.org/1999/xhtml"><head><meta http-equiv="Content-Type" content="text/html; charset=utf-8" /><title>Hamsi Manager</title></head><body>' +
                         '<center>' +
                         '<form action="http://hamsiapps.com/ForMyProjects/ReportBug.php" method="post">' +
                         '<TABLE><TR><TD valign="top">%s'
                         '</TD><TD colspan=2><textarea ROWS="7" COLS="40" name="userNotes"></textarea></TD></TR></TABLE>' +
                         '<TABLE><TR><TD valign="top" colspan=2>%s</TD><TD align="right"><input type="search" name="nameAndSurname" value=""></input></TD></TR>' +
                         '<TR><TD valign="top" colspan=2>%s</TD><TD align="right"><input type="search" name="mail" value=""></input></TD></TR></TABLE>' +
                         '<TABLE><TR><TD align="right"><input name="send" type="submit" value="&nbsp;&nbsp;&nbsp;%s&nbsp;&nbsp;&nbsp;&nbsp;"></TD></TR></TABLE>' +
                         '<INPUT TYPE="hidden" name="error" value="%s" />' +
                         '<INPUT TYPE="hidden" name="thankYouMessages" value="%s" />' +
                         '<INPUT TYPE="hidden" name="p" value="HamsiManager" />' +
                         '<INPUT TYPE="hidden" name="l" value="' + str(language) + '" />' +
                         '<INPUT TYPE="hidden" name="v" value="' + str(uni.intversion) + '" /></form>' +
                         '%s</center></body></html>'
                     ) % (
                         str(translate("ReportBug",
                                       "<b>Error description :</b> <br>(Be can null)<br><b>Note:</b>Please write what you did before you received the error here.")),
                         str(translate("ReportBug", "<b>Name and Surname :</b> (Be can null)")),
                         str(translate("ReportBug",
                                       "<b>E-mail address :</b> (Be can null)<br><b>Note:</b>Will be kept strictly confidential. It will be used solely to report you back once the problem is solved..")),
                         str(translate("ReportBug", "Report Bug")),
                         _errorDetails,
                         str(translate("ReportBug",
                                       "Thank you for sending us your error report. You have already contributed a lot to make the next release even better..<br>")),
                         _errorDetails)
        if self.pathOfReportFile is None:
            import random

            self.pathOfReportFile = fu.joinPath(fu.getTempDir(), "HamsiManager-ErrorOutput-" + str(
                random.randrange(0, 1000000)) + ".html")
            fu.writeToFile(self.pathOfReportFile, htmlString)


class ReportBugDialog(MDialog):
    global isClose

    def __init__(self, _errorDetails="", _pathOfReportFile=None):
        global isClose
        currentMainWindow = getMainWindow()
        if uni.isStartingSuccessfully:
            isShowFixMe = False
        else:
            isShowFixMe = True
        if currentMainWindow is None:
            setMainWindow(self)
        try: MDialog.__init__(self, currentMainWindow)
        except: MDialog.__init__(self, None)
        self.pathOfReportFile = _pathOfReportFile
        self.namMain = None
        self.nrqPost = None
        self.nrpBack = None
        isClose = False
        try:
            if isActivePyKDE4:
                self.setButtons(MDialog.NoDefault)
        except: pass

        try:
            if Dialogs.pnlState is not None:
                Dialogs.showState("", 1, 1)
        except: pass
        pnlMain = MWidget(self)
        self.vblMain = MVBoxLayout(pnlMain)
        self.pbtnSendAndClose = MPushButton(translate("ReportBug", "Send And Close"))
        self.pbtnCancel = MPushButton(translate("ReportBug", "Cancel"))
        self.connect(self.pbtnSendAndClose, SIGNAL("clicked()"), self.sendAndClose)
        self.connect(self.pbtnCancel, SIGNAL("clicked()"), self.cancel)
        self.pbtnShowDetailsPage = MPushButton(translate("ReportBug", "Show Details File"))
        self.pbtnCheckUpdate = MPushButton(translate("ReportBug", "Check Update"))
        self.cckbIsSendTableContents = Options.MyCheckBox(self, translate("ReportBug",
                                                                          "Send Table Contents For More Details"), 0,
                                                          _stateChanged=self.isSendTableContents)
        self.teErrorDetails = MTextEdit()
        try:
            self.teErrorDetails.setHtml(str(_errorDetails.replace("<hr>", "")))
        except:
            self.teErrorDetails.setHtml(translate("ReportBug",
                                                  "I cannot send the error details due to some character errors.<br>To see the details, please click on the \"Show details file\" button."))
            self.teErrorDetails.setEnabled(False)
        self.connect(self.pbtnShowDetailsPage, SIGNAL("clicked()"), self.showDetailsPage)
        self.connect(self.pbtnCheckUpdate, SIGNAL("clicked()"), self.checkUpdate)
        self.teErrorDetails.setMinimumHeight(220)
        self.vblMain.addWidget(self.teErrorDetails, 20)
        self.vblMain.addWidget(self.cckbIsSendTableContents, 1)
        lblUserNotes = MLabel(translate("ReportBug", "Notes : "))
        lblName = MLabel(translate("ReportBug", "Name And Surname : "))
        lblEMailAddress = MLabel(translate("ReportBug", "E-mail Address : "))
        lblAlert = MLabel(translate("ReportBug",
                                    "Note : Will be kept strictly confidential. It will be used solely to learn information about of your report."))
        self.teUserNotes = MTextEdit(self)
        self.leName = MLineEdit(self)
        self.leEMailAddress = MLineEdit(self)
        hbox1 = MHBoxLayout()
        hbox1.addWidget(lblUserNotes, 1)
        hbox1.addWidget(self.teUserNotes, 20)
        hbox2 = MHBoxLayout()
        hbox2.addWidget(lblName, 1)
        hbox2.addWidget(self.leName, 20)
        hbox3 = MHBoxLayout()
        hbox3.addWidget(lblEMailAddress, 1)
        hbox3.addWidget(self.leEMailAddress, 20)
        hbox0 = MHBoxLayout()
        hbox0.addWidget(self.pbtnShowDetailsPage, 1)
        hbox0.addWidget(self.pbtnCheckUpdate, 1)
        hbox0.addStretch(2)
        hbox0.addWidget(self.pbtnSendAndClose, 1)
        hbox0.addWidget(self.pbtnCancel, 1)
        VBox1 = MVBoxLayout()
        VBox1.addLayout(hbox2)
        VBox1.addLayout(hbox3)
        VBox1.addWidget(lblAlert)
        gboxContactInformations = MGroupBox(translate("ReportBug", "Contact Informations : "))
        gboxContactInformations.setLayout(VBox1)
        self.vblMain.addLayout(hbox1, 1)
        self.vblMain.addWidget(gboxContactInformations, 1)
        self.vblMain.addLayout(hbox0, 1)
        try:
            if isActivePyKDE4:
                self.setMainWidget(pnlMain)
            else:
                self.setLayout(self.vblMain)
        except:
            self.setLayout(self.vblMain)
        self.setWindowTitle(translate("ReportBug", "Please Report This Bug!.."))
        self.setMaximumSize(600, 375)
        self.show()
        self.setMaximumSize(10000, 10000)
        if isShowFixMe and isQuickMake is False and uni.loggingLevel != logging.DEBUG:
            try:
                answer = Dialogs.askSpecial(translate("ReportBug", "I Have A Suggestion!"),
                                            translate("ReportBug", "<b>Please check the following: ;</b><br>" +
                                                      "<b>1-)</b>If you have received this error when you were checking the last folder, reset the \"Last Directory\",<br>" +
                                                      "<b>2-)</b>If you have received this error due to your changed settings, reset the \"Settings\",<br>" +
                                                      "<b>3-)</b>If you continue to receive this error even after resetting the settings, reset \"All\".<br>" +
                                                      "<br><b>You can enable Hamsi Manager to run as normal.<br>Please take a moment to send us the error report.</b>"),
                                            translate("ReportBug", "Last Directory"),
                                            translate("ReportBug", "All"),
                                            translate("ReportBug", "Settings"),
                                            translate("ReportBug", "Ignore"))
                if answer == translate("ReportBug", "Last Directory"):
                    Settings.setting().setValue("lastDirectory", trQVariant(fu.userDirectoryPath))
                elif answer == translate("ReportBug", "Settings"):
                    Settings.reFillSettings(True)
                elif answer == translate("ReportBug", "All"):
                    Settings.reFillAll(True)
            except: pass

    def sendAndClose(self):
        uni.isCanBeShowOnMainWindow = False
        language = "en_GB"
        if "language" in uni.MySettings:
            language = uni.MySettings["language"]
        self.namMain = MNetworkAccessManager(self)
        self.connect(self.namMain, SIGNAL("finished (QNetworkReply *)"), self.sendFinished)
        self.nrqPost = MNetworkRequest(MUrl("http://hamsiapps.com/ForMyProjects/ReportBug.php"))
        self.nrpBack = self.namMain.post(self.nrqPost,
                                         "p=HamsiManager&l=" + str(language) + "&v=" + str(uni.intversion) +
                                         "&thankYouMessages=new style" +
                                         "&userNotes=" + Organizer.quote(str(self.teUserNotes.toHtml())) +
                                         "&error=" + Organizer.quote(str(self.teErrorDetails.toHtml())) +
                                         "&nameAndSurname=" + Organizer.quote(str(self.leName.text())) +
                                         "&mail=" + Organizer.quote(str(self.leEMailAddress.text()))
        )
        self.connect(self.nrpBack, SIGNAL("downloadProgress (qint64,qint64)"), self.sending)
        Dialogs.showState(translate("ReportBug", "Sending Your Report"), 0, 100, True, self.cancelSending)

    def sending(self, _currentValue, _maxValue):
        Dialogs.showState(translate("ReportBug", "Sending Your Report"), _currentValue, _maxValue, True,
                          self.cancelSending)

    def cancelSending(self):
        if self.nrpBack is not None:
            self.nrpBack.abort()

    def sendFinished(self, _nrpBack):
        Dialogs.showState(translate("ReportBug", "Sending Your Report"), 100, 100)
        if _nrpBack.error() == MNetworkReply.NoError:
            Dialogs.show(translate("ReportBug", "Report Received Successfully"), translate("ReportBug",
                                                                                           "Thank you for sending us your report. You have contributed a lot to make the next release even better."))
            self.close()
        elif _nrpBack.error() == MNetworkReply.OperationCanceledError:
            Dialogs.show(translate("ReportBug", "Report Sending Canceled"),
                         translate("ReportBug", "Report sending canceled successfully."))
        else:
            Dialogs.show(translate("ReportBug", "An Error Has Occurred."),
                         translate("ReportBug", "An unknown error has occurred. Please try again."))
        uni.isCanBeShowOnMainWindow = True
        self.namMain = None
        self.nrqPost = None
        self.nrpBack = None

    def cancel(self):
        if self.nrpBack is not None:
            self.nrpBack.abort()
        self.close()

    def checkUpdate(self):
        from Core import UpdateControl

        UpdateControl.UpdateControl(self)

    def closeEvent(self, _event):
        global isClose
        isClose = True
        try:
            self.close()
            if uni.isStartingSuccessfully is False:
                self.parent().close()
        except: pass

    def showDetailsPage(self):
        from Details import HtmlDetails

        HtmlDetails.HtmlDetails(self.pathOfReportFile)

    def isSendTableContents(self):
        try:
            currentText = str(self.teErrorDetails.toHtml())
            if self.cckbIsSendTableContents.checkState() == Mt.Checked:
                currentDirectoryPath = ""
                try: currentDirectoryPath = getMainWindow().FileManager.getCurrentDirectoryPath()
                except: pass
                settingText = "<p><b>" + str(
                    translate("ReportBug", "Contents Directory : ")) + "</b>" + currentDirectoryPath + "</p>"
                settingText += "<p><h3>" + str(translate("ReportBug", "Table Contents : ")) + "</h3>"
                try:
                    settingText += getMainTable().exportValues("return", "html", "no")
                except: pass
                settingText += "<hr><p><h3>" + str(
                    translate("ReportBug", "File Information : ")) + "</h3><table border=1>"
                try:
                    for rowValues in getMainTable().values:
                        settingText += "<tr><td>" + str(
                            uni.trUnicode(rowValues["path"], fu.fileSystemEncoding)) + "</td></tr>"
                    settingText += "</table></p><hr><p><h3>" + str(translate("ReportBug", "File Details : ")) + "</h3>"
                    if len(getMainTable().values) > 0:
                        settingText += "<table border=1><tr>"
                        for key, value in getMainTable().values[0].items():
                            settingText += "<td><b>" + key + "</b></td>"
                        settingText += "</tr>"
                        for rowValues in getMainTable().values:
                            settingText += "<tr>"
                            for key, value in rowValues.items():
                                settingText += "<td>" + str(value) + "</td>"
                            settingText += "</tr>"
                        settingText += "</table>"
                except: pass
                self.teErrorDetails.setHtml(str(
                    currentText + "<br>----------------------////////----------------------<br><br><a name='tableContents'><b>" + str(
                        translate("ReportBug",
                                  "Note : You can check and delete your personal informations.")) + "</b></a>" + settingText))
                self.teErrorDetails.scrollToAnchor("tableContents")
            else:
                currentText = currentText.split("----------------------////////----------------------")[0]
                self.teErrorDetails.setHtml(str(currentText))
        except:
            pass
        
        
        
        
