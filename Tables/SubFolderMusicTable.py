## This file is part of HamsiManager.
## 
## Copyright (c) 2010 - 2013 Murat Demir <mopened@gmail.com>      
##
## Hamsi Manager is free software; you can redistribute it and/or modify
## it under the terms of the GNU General Public License as published by
## the Free Software Foundation; either version 2 of the License, or
## (at your option) any later version.
## 
## Hamsi Manager is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU General Public License for more details.
## 
## You should have received a copy of the GNU General Public License
## along with HamsiManager; if not, write to the Free Software
## Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA

from Core import Organizer
import InputOutputs
import SearchEngines
from Core.MyObjects import *
from Details import MusicDetails
from Core import Universals
from Core import Variables
from Core import Dialogs
import Options
import Taggers
from time import gmtime
from Core import Records
from Core import ReportBug

class SubFolderMusicTable():
    def __init__(self, _table):
        self.Table = _table
        self.keyName = "music"
        self.hiddenTableColumnsSettingKey = "hiddenSubFolderMusicTableColumns"
        self.refreshColumns()
        pbtnVerifyTableValues = MPushButton(translate("SubFolderMusicTable", "Verify Table"))
        pbtnVerifyTableValues.setMenu(SearchEngines.SearchEngines(self.Table))
        self.Table.mContextMenu.addMenu(SearchEngines.SearchEngines(self.Table, True))
        self.isPlayNow = MToolButton()
        self.isPlayNow.setToolTip(translate("SubFolderMusicTable", "Play Now"))
        self.isPlayNow.setIcon(MIcon("Images:playNow.png"))
        self.isPlayNow.setCheckable(True)
        self.isPlayNow.setAutoRaise(True)
        self.isPlayNow.setChecked(Universals.getBoolValue("isPlayNow"))
        self.Table.hblBox.insertWidget(self.Table.hblBox.count()-3, self.isPlayNow)
        self.Table.hblBox.insertWidget(self.Table.hblBox.count()-1, pbtnVerifyTableValues)
        
    def readContents(self, _directoryPath):
        currentTableContentValues = []
        musicFileNames = InputOutputs.readDirectoryWithSubDirectoriesThread(_directoryPath, 
                    int(Universals.MySettings["subDirectoryDeep"]), "music", Universals.getBoolValue("isShowHiddensInSubFolderMusicTable"))
        isCanNoncompatible = False
        allItemNumber = len(musicFileNames)
        Universals.startThreadAction()
        for musicNo,musicName in enumerate(musicFileNames):
            isContinueThreadAction = Universals.isContinueThreadAction()
            if isContinueThreadAction:
                try:
                    if InputOutputs.isReadableFileOrDir(musicName, False, True):
                        tagger = Taggers.getTagger()
                        try:
                            tagger.loadFile(musicName)
                        except:
                            Dialogs.showError(translate("InputOutputs/Musics", "Incorrect Tag"), 
                                str(translate("InputOutputs/Musics", "\"%s\" : this file has the incorrect tag so can't read tags.")
                                ) % Organizer.getLink(musicName))
                        if tagger.isAvailableFile() == False:
                            isCanNoncompatible=True
                        content = {}
                        content["path"] = musicName
                        content["baseNameOfDirectory"] = str(str(InputOutputs.getBaseName(_directoryPath)) + str(InputOutputs.getDirName(musicName)).replace(_directoryPath,""))
                        content["baseName"] = InputOutputs.getBaseName(musicName)
                        content["artist"] = tagger.getArtist()
                        content["title"] = tagger.getTitle()
                        content["album"] = tagger.getAlbum()
                        content["trackNum"] = tagger.getTrackNum()
                        content["year"] = tagger.getYear()
                        content["genre"] = tagger.getGenre()
                        content["firstComment"] = tagger.getFirstComment()
                        content["firstLyrics"] = tagger.getFirstLyrics()
                        currentTableContentValues.append(content)
                except:
                    ReportBug.ReportBug()
            else:
                allItemNumber = musicNo+1
            Dialogs.showState(translate("InputOutputs/Musics", "Reading Music Tags"),musicNo+1,allItemNumber, True)
            if isContinueThreadAction==False:
                break
        Universals.finishThreadAction()
        if isCanNoncompatible == True:
            Dialogs.show(translate("InputOutputs/Musics", "Possible ID3 Mismatch"),
                translate("InputOutputs/Musics", "Some of the files presented in the table may not support ID3 technology.<br>Please check the files and make sure they support ID3 information before proceeding."))
        return currentTableContentValues
    
    def writeContents(self):
        self.Table.changedValueNumber = 0
        changingFileDirectories=[]
        changingTags=[]
        isMovedToNewDirectory = False
        currentDirectoryPath = ""
        newDirectoryPath = ""
        if Variables.isActiveAmarok and Universals.getBoolValue("isSubFolderMusicTableValuesChangeInAmarokDB"):
            import Amarok
            if Amarok.checkAmarok(True, False) == False:
                return False
        Universals.startThreadAction()
        allItemNumber = len(self.Table.currentTableContentValues)
        Dialogs.showState(translate("InputOutputs/Musics", "Writing Music Tags"),0,allItemNumber, True)
        for rowNo in range(self.Table.rowCount()):
            isContinueThreadAction = Universals.isContinueThreadAction()
            if isContinueThreadAction:
                try:
                    changingTag = {"path" : self.Table.currentTableContentValues[rowNo]["path"]}
                    if InputOutputs.isWritableFileOrDir(self.Table.currentTableContentValues[rowNo]["path"], False, True):
                        if self.Table.isRowHidden(rowNo):
                            InputOutputs.removeFileOrDir(self.Table.currentTableContentValues[rowNo]["path"])
                            self.Table.changedValueNumber += 1
                        else:
                            baseNameOfDirectory = str(self.Table.currentTableContentValues[rowNo]["baseNameOfDirectory"])
                            baseName = str(self.Table.currentTableContentValues[rowNo]["baseName"])
                            tagger = Taggers.getTagger()
                            tagger.loadFileForWrite(self.Table.currentTableContentValues[rowNo]["path"])
                            isCheckLike = Taggers.getSelectedTaggerTypeForRead()==Taggers.getSelectedTaggerTypeForWrite()
                            if self.Table.isChangableItem(rowNo, 2, self.Table.currentTableContentValues[rowNo]["artist"], True, isCheckLike):
                                value = str(self.Table.item(rowNo,2).text())
                                tagger.setArtist(value)
                                changingTag["artist"] = value
                                Records.add(str(translate("SubFolderMusicTable", "Artist")), str(self.Table.currentTableContentValues[rowNo]["artist"]), value)
                                self.Table.changedValueNumber += 1
                            if self.Table.isChangableItem(rowNo, 3, self.Table.currentTableContentValues[rowNo]["title"], True, isCheckLike):
                                value = str(self.Table.item(rowNo,3).text())
                                tagger.setTitle(value)
                                changingTag["title"] = value
                                Records.add(str(translate("SubFolderMusicTable", "Title")), str(self.Table.currentTableContentValues[rowNo]["title"]), value)
                                self.Table.changedValueNumber += 1
                            if self.Table.isChangableItem(rowNo, 4, self.Table.currentTableContentValues[rowNo]["album"], True, isCheckLike):
                                value = str(self.Table.item(rowNo,4).text())
                                tagger.setAlbum(value)
                                changingTag["album"] = value
                                Records.add(str(translate("SubFolderMusicTable", "Album")), str(self.Table.currentTableContentValues[rowNo]["album"]), value)
                                self.Table.changedValueNumber += 1
                            if self.Table.isChangableItem(rowNo, 5, self.Table.currentTableContentValues[rowNo]["trackNum"], True, isCheckLike):
                                value = str(self.Table.item(rowNo,5).text())
                                tagger.setTrackNum(value)
                                changingTag["trackNum"] = value
                                Records.add(str(translate("SubFolderMusicTable", "Track No")), str(self.Table.currentTableContentValues[rowNo]["trackNum"]), value)
                                self.Table.changedValueNumber += 1
                            if self.Table.isChangableItem(rowNo, 6, self.Table.currentTableContentValues[rowNo]["year"], True, isCheckLike):
                                value = str(self.Table.item(rowNo,6).text())
                                tagger.setDate(value)
                                changingTag["year"] = value
                                Records.add(str(translate("SubFolderMusicTable", "Year")), str(self.Table.currentTableContentValues[rowNo]["year"]), value)
                                self.Table.changedValueNumber += 1
                            if self.Table.isChangableItem(rowNo, 7, self.Table.currentTableContentValues[rowNo]["genre"], True, isCheckLike):
                                value = str(self.Table.item(rowNo,7).text())
                                tagger.setGenre(value)
                                changingTag["genre"] = value
                                Records.add(str(translate("SubFolderMusicTable", "Genre")), str(self.Table.currentTableContentValues[rowNo]["genre"]), value)
                                self.Table.changedValueNumber += 1
                            if self.Table.isChangableItem(rowNo, 8, self.Table.currentTableContentValues[rowNo]["firstComment"], True, isCheckLike):
                                value = str(self.Table.item(rowNo,8).text())
                                tagger.setFirstComment(value)
                                changingTag["firstComment"] = value
                                Records.add(str(translate("SubFolderMusicTable", "Comment")), str(self.Table.currentTableContentValues[rowNo]["firstComment"]), value)
                                self.Table.changedValueNumber += 1
                            if len(self.Table.tableColumns)>9 and self.Table.isChangableItem(rowNo, 9, self.Table.currentTableContentValues[rowNo]["firstLyrics"], True, isCheckLike):
                                value = str(self.Table.item(rowNo,9).text())
                                tagger.setFirstLyrics(value)
                                changingTag["firstLyrics"] = value
                                Records.add(str(translate("SubFolderMusicTable", "Lyrics")), str(self.Table.currentTableContentValues[rowNo]["firstLyrics"]), value)
                                self.Table.changedValueNumber += 1
                            if len(changingTag)>1:
                                changingTags.append(changingTag)
                            tagger.update()
                            if self.Table.isChangableItem(rowNo, 0, baseNameOfDirectory):
                                baseNameOfDirectory = str(self.Table.item(rowNo,0).text())
                                self.Table.changedValueNumber += 1
                                isMovedToNewDirectory = True
                                currentDirectoryPath = InputOutputs.getDirName(self.Table.currentTableContentValues[rowNo]["path"])
                                newDirectoryPath = InputOutputs.joinPath(InputOutputs.getDirName(InputOutputs.getDirName(self.Table.currentTableContentValues[rowNo]["path"])), baseNameOfDirectory)
                                self.Table.setNewDirectory(newDirectoryPath)
                            if self.Table.isChangableItem(rowNo, 1, baseName, False):
                                baseName = str(self.Table.item(rowNo,1).text())
                                self.Table.changedValueNumber += 1
                            newFilePath = InputOutputs.joinPath(str(self.Table.currentTableContentValues[rowNo]["path"]).replace(InputOutputs.joinPath(str(self.Table.currentTableContentValues[rowNo]["baseNameOfDirectory"]), str(self.Table.currentTableContentValues[rowNo]["baseName"])), ""), baseNameOfDirectory, baseName)
                            if InputOutputs.getRealPath(self.Table.currentTableContentValues[rowNo]["path"]) != InputOutputs.getRealPath(newFilePath):
                                changingFileDirectories.append([self.Table.currentTableContentValues[rowNo]["path"], 
                                                                InputOutputs.getRealPath(newFilePath)])
                except:
                    ReportBug.ReportBug()
            else:
                allItemNumber = rowNo+1
            Dialogs.showState(translate("InputOutputs/Musics", "Writing Music Tags"),rowNo+1,allItemNumber, True)
            if isContinueThreadAction==False:
                break
        Universals.finishThreadAction()
        pathValues = InputOutputs.changeDirectories(changingFileDirectories)
        if Variables.isActiveAmarok and Universals.getBoolValue("isSubFolderMusicTableValuesChangeInAmarokDB"):
            import Amarok
            from Amarok import Operations
            Operations.changeTags(changingTags)
            Operations.changePaths(pathValues, "file")
        return True
        
    def showDetails(self, _fileNo, _infoNo):
        MusicDetails.MusicDetails(self.Table.currentTableContentValues[_fileNo]["path"], Universals.getBoolValue("isOpenDetailsInNewWindow"), self.isPlayNow.isChecked())
    
    def cellClicked(self,_row,_column):
        currentItem = self.Table.currentItem()
        if currentItem is not None:
            cellLenght = len(currentItem.text())*8
            if cellLenght > self.Table.columnWidth(_column):
                self.Table.setColumnWidth(_column,cellLenght)
            if _column==8 or _column==9:
                if self.Table.rowHeight(_row)<150:
                    self.Table.setRowHeight(_row,150)
                if self.Table.columnWidth(_column)<250:
                    self.Table.setColumnWidth(_column,250)
        
    def cellDoubleClicked(self,_row,_column):
        try:
            if _column==8 or _column==9:
                self.showDetails(_row, _column)
            else:
                if Universals.getBoolValue("isRunOnDoubleClick"):
                    self.showDetails(_row, _column)
        except:
            Dialogs.showError(translate("SubFolderMusicTable", "Cannot Open Music File"), 
                        str(translate("SubFolderMusicTable", "\"%s\" : cannot be opened. Please make sure that you selected a music file.")
                        ) % Organizer.getLink(self.Table.currentTableContentValues[_row]["path"]))
       
    def refreshColumns(self):
        self.Table.tableColumns = Taggers.getAvailableLabelsForTable()
        self.Table.tableColumnsKey = Taggers.getAvailableKeysForTable()
        
    def save(self):
        self.Table.checkFileExtensions(1, "baseName")
        MusicDetails.MusicDetails.closeAllMusicDialogs()
        return self.writeContents()
        
    def refresh(self, _path):
        self.Table.setColumnWidth(5,70)
        self.Table.setColumnWidth(6,40)
        self.Table.currentTableContentValues = self.readContents(_path)
        self.Table.setRowCount(len(self.Table.currentTableContentValues))
        allItemNumber = self.Table.rowCount()
        for rowNo in range(allItemNumber):
            for itemNo in range(len(self.Table.tableColumns)):
                item = None
                if itemNo==0:
                    newString = Organizer.emend(self.Table.currentTableContentValues[rowNo]["baseNameOfDirectory"], "directory")
                    item = self.Table.createTableWidgetItem(newString, self.Table.currentTableContentValues[rowNo]["baseNameOfDirectory"])
                elif itemNo==1:
                    newString = Organizer.emend(self.Table.currentTableContentValues[rowNo]["baseName"], "file")
                    item = self.Table.createTableWidgetItem(newString, self.Table.currentTableContentValues[rowNo]["baseName"])
                elif itemNo==2:
                    newString = Organizer.emend(self.Table.currentTableContentValues[rowNo]["artist"])
                    item = self.Table.createTableWidgetItem(newString, self.Table.currentTableContentValues[rowNo]["artist"])
                elif itemNo==3:
                    newString = Organizer.emend(self.Table.currentTableContentValues[rowNo]["title"])
                    item = self.Table.createTableWidgetItem(newString, self.Table.currentTableContentValues[rowNo]["title"])
                elif itemNo==4:
                    newString = Organizer.emend(self.Table.currentTableContentValues[rowNo]["album"])
                    item = self.Table.createTableWidgetItem(newString, self.Table.currentTableContentValues[rowNo]["album"])
                elif itemNo==5:
                    newString = str(self.Table.currentTableContentValues[rowNo]["trackNum"])
                    item = self.Table.createTableWidgetItem(newString, self.Table.currentTableContentValues[rowNo]["trackNum"])
                elif itemNo==6:
                    newString = Organizer.emend(self.Table.currentTableContentValues[rowNo]["year"])
                    item = self.Table.createTableWidgetItem(newString, self.Table.currentTableContentValues[rowNo]["year"])
                elif itemNo==7:
                    newString = Organizer.emend(self.Table.currentTableContentValues[rowNo]["genre"])
                    item = self.Table.createTableWidgetItem(newString, self.Table.currentTableContentValues[rowNo]["genre"])
                elif itemNo==8:
                    newString = Organizer.emend(self.Table.currentTableContentValues[rowNo]["firstComment"])
                    item = self.Table.createTableWidgetItem(newString, self.Table.currentTableContentValues[rowNo]["firstComment"])
                elif itemNo==9:
                    newString = Organizer.emend(self.Table.currentTableContentValues[rowNo]["firstLyrics"])
                    item = self.Table.createTableWidgetItem(newString, self.Table.currentTableContentValues[rowNo]["firstLyrics"])
                if item!=None:
                    self.Table.setItem(rowNo, itemNo, item)
            Dialogs.showState(translate("InputOutputs/Tables", "Generating Table..."), rowNo+1, allItemNumber) 
                        
    def correctTable(self):
        for rowNo in range(self.Table.rowCount()):
            for itemNo in range(self.Table.columnCount()):
                if self.Table.isChangableItem(rowNo, itemNo):
                    if itemNo==0:
                        newString = Organizer.emend(str(self.Table.item(rowNo,itemNo).text()), "directory")
                    elif itemNo==1:
                        newString = Organizer.emend(str(self.Table.item(rowNo,itemNo).text()), "file")
                    else:
                        newString = Organizer.emend(str(self.Table.item(rowNo,itemNo).text()))
                    self.Table.item(rowNo,itemNo).setText(trForUI(newString))
          
    def getValueByRowAndColumn(self, _rowNo, _columnNo):
        if _columnNo==0:
            return self.Table.currentTableContentValues[_rowNo]["baseNameOfDirectory"]
        elif _columnNo==1:
            return self.Table.currentTableContentValues[_rowNo]["baseName"]
        elif _columnNo==2:
            return self.Table.currentTableContentValues[_rowNo]["artist"]
        elif _columnNo==3:
            return self.Table.currentTableContentValues[_rowNo]["title"]
        elif _columnNo==4:
            return self.Table.currentTableContentValues[_rowNo]["album"]
        elif _columnNo==5:
            return self.Table.currentTableContentValues[_rowNo]["trackNum"]
        elif _columnNo==6:
            return self.Table.currentTableContentValues[_rowNo]["year"]
        elif _columnNo==7:
            return self.Table.currentTableContentValues[_rowNo]["genre"]
        elif _columnNo==8:
            return self.Table.currentTableContentValues[_rowNo]["firstComment"]
        elif _columnNo==9:
            return self.Table.currentTableContentValues[_rowNo]["firstLyrics"]
        return ""