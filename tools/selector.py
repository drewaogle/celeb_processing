#!/usr/bin/env python3

import sys
from os import listdir
from os.path import isfile,join,exists,basename
from PyQt5.QtWidgets import QApplication,QLabel,QVBoxLayout,QHBoxLayout,QWidget,QLabel,QSpacerItem,QSizePolicy,QFrame 
from PyQt5.QtGui import QPixmap,QScreen,QPainter,QColor
#import PyQt5.QtCore
from PyQt5.QtCore import Qt


def FacePathGeneration(self):
     for element in listdir("."):
        element_path = join(".",element)
        if not isfile( element_path ):
            print(f"- Processing {element} as {element_path}")
            element_path = join( element_path , "processed" )
            if not exists( element_path ):
                continue
            for celeb_element in listdir(element_path):
                celeb_element_path = join(element_path,celeb_element)
                #if celeb_element[-4:] == ".jpg":
                if isfile(celeb_element_path) and celeb_element[-4:] == ".jpg":
                    face_dir = "{0}_aligned".format( celeb_element[:-4] )
                    face_dir_path = join( element_path, face_dir )
                    yield (element,celeb_element_path,face_dir_path)


class SelectableFace(QLabel):
    def __init__(self):
        super(SelectableFace,self).__init__()
        self.current = False # current - the face which the user is interacting with
        self.selected = False # is a valid face for the selection criteria
        self.poor_quality = False # not a good face for any kind of training
        self.path = None # image path
        self.setStyleSheet('')
        self.boxColor = QColor(0,0,0) # black
        self.textColor = QColor(255,255,255) # white
    def setImagePath(self,path):
        self.path = path
        self.setPixmap( QPixmap( path ))
    def getImagePath(self):
        return self.path
    def setActive(self,isCurrent):
        self.current = isCurrent
        self.updateColor()
    def setSelected(self,isSelected):
        self.selected = isSelected
        self.updateColor()
    def togglePoorQuality(self):
        self.poor_quality = not self.poor_quality
        self.updateColor()
    def setPoorQuality(self,isPoorQuality):
        self.poor_quality = isPoorQuality
        self.updateColor()
    def toggleSelected(self):
        self.selected = not self.selected
        self.updateColor()
    def isSelected(self):
        return self.selected
    def isPoorQuality(self):
        return self.poor_quality
    def xpaintEvent(self, event):
        super(SelectableFace,self).paintEvent(event)
        painter = QPainter()
        painter.begin(self)
        painter.setBrush(self.boxColor)
        size = self.size()
        xoffset = size.height() - 20
#        painter.drawRect( xoffset,0,20, size.width())
        painter.drawRect( 0,xoffset, size.width(), 20)
        painter.end()

    def updateColor(self):
        if self.selected:
            color = "purple" if self.current else "green"
        else:
            color = "blue" if self.current else "red"
        self.setStyleSheet(f'padding:3px; background-color: {color};')
        self.setText( "V" if self.poor_quality else "" )


class SelectorWindow(QWidget):
    def __init__(self):
        super(SelectorWindow,self).__init__()
        self.selection = FacePathGeneration(".")
        self.mainvbox = QVBoxLayout()
        self.imagecomparebox = QHBoxLayout()
        self.facebox = QVBoxLayout()

        self.outputlabel = QLabel()
        self.outputlabel.setScaledContents(True)
        self.facelabels = []
        self.statuslabel = QLabel("Status Layout")
        self.imagecomparebox.addWidget(self.outputlabel)
        self.imagecomparebox.addLayout(self.facebox)
        self.mainvbox.addWidget(self.statuslabel)
        self.mainvbox.addLayout(self.imagecomparebox)
        self.setLayout(self.mainvbox)

        topSpacer = QSpacerItem(20,40,QSizePolicy.Minimum,QSizePolicy.Expanding)
        bottomSpacer = QSpacerItem(20,40,QSizePolicy.Minimum,QSizePolicy.Expanding)
        self.facebox.addItem(topSpacer)
        self.facebox.addItem(bottomSpacer)
        self.activeFace = 1
        self.faceCount = 0
        self.findNext()
        self.show()
        self.setFixedSize(1000,1000)
    def setup( self, element, celeb_element_path,face_dir_path ):
        face_count = len( [ f for f in listdir( face_dir_path ) if isfile( join( face_dir_path, f )) ] )
        face_plural = "faces" if face_count != 1 else "face"
        print(f"{face_count} {face_plural}")
        self.outputlabel.setPixmap(QPixmap( celeb_element_path))
        [ facelabel.hide() for facelabel in self.facelabels ]
        [ facelabel.setSelected(False) for facelabel in self.facelabels ]
        fnum =0
        for fimg in listdir( face_dir_path ):
            fnum = fnum + 1
            if len( self.facelabels ) < fnum :
                l = SelectableFace()
                self.facebox.insertWidget(fnum,l)
                self.facelabels.append(l)
            self.facelabels[fnum-1].setImagePath(join( face_dir_path, fimg ))
            self.facelabels[fnum-1].setSelected(True)
            self.facelabels[fnum-1].setPoorQuality(False)
            self.facelabels[fnum-1].setActive(fnum == 1)
            self.facelabels[fnum-1].show()
        #mainvbox.show()
        self.faceCount = face_count
        self.activeFace = 1
        self.statuslabel.show()
        self.outputlabel.show()

        celeb_picture_number = basename(celeb_element_path)[:-4]

        self.statuslabel.setText(f"Celeb: {element}, Image: {celeb_picture_number}")
        self.celeb_name = element
        self.picture_id = celeb_picture_number

        if self.faceCount == 0:
            self.saveOutput()

    def findNext(self):
        try:
            self.setup( *next(self.selection))
            while self.outputExists():
                self.setup( *next(self.selection))
        except StopIteration:
            print("All Images Labeled")
            self.deleteLater()
    # outputs csv
    # command, ...
    # status,[ok,failed]
    #  ok = processed ok
    #  failed = failed to process
    # image,path,is_celeb,poor_quality
    def outputExists(self):
        return exists( f"{self.celeb_name}_{self.picture_id}.csv")
    def saveOutput(self):
        filename = f"{self.celeb_name}_{self.picture_id}.csv"
        print( f"Saving {filename}")
        fp = open( filename, "w")
        fp.write( "status,{}\n".format( "ok" if self.faceCount != 0 else "failed"))
        facenum = 0
        while facenum < self.faceCount:
            face = self.facelabels[ facenum ]
            is_celeb = face.isSelected()
            is_poor_quality = face.isPoorQuality()
            fp.write( "image,{},{},{}\n".format( face.getImagePath(),is_celeb,is_poor_quality))
            facenum = facenum + 1
        fp.close()


    def keyPressEvent(self,event):
        if event.key() == Qt.Key_Q:
            print("Exiting")
            self.deleteLater()
            sys.exit(1)
        elif event.key() == Qt.Key_X:
            print("Deselecting All")
            [ facelabel.setSelected(False) for facelabel in self.facelabels ]

        elif event.key() == Qt.Key_1:
            print("Selecting Item 1")
        elif event.key() == Qt.Key_Space:
            print(f"Toggling Selection on Current Item {self.activeFace}")
            self.facelabels[self.activeFace-1].toggleSelected()
        elif event.key() == Qt.Key_V:
            print(f"Toggling Poor Quality on Current Item {self.activeFace}")
            self.facelabels[self.activeFace-1].togglePoorQuality()
        elif event.key() == Qt.Key_Up:
            self.facelabels[self.activeFace-1].setActive(False)
            self.activeFace = max( 0, self.activeFace-1)
            self.facelabels[self.activeFace-1].setActive(True)

        elif event.key() == Qt.Key_Down:
            self.facelabels[self.activeFace-1].setActive(False)
            self.activeFace = min( self.faceCount, self.activeFace+1)
            self.facelabels[self.activeFace-1].setActive(True)
        elif event.key() == Qt.Key_P:
            print(f"Accepting {self.faceCount} to check")
            fnum = 0
            while fnum < self.faceCount:
                accepted = "Accepted" if self.facelabels[fnum].isSelected() else "Rejected"
                print(f"Face {fnum}: {accepted}")
                fnum = fnum + 1
            self.saveOutput()
            self.findNext()


app = QApplication([])
# primary is showing wacky on extended desktop through VcXsvr
print("Screen geometry = {0}".format( QApplication.primaryScreen().availableGeometry()))
for s in QApplication.screens():
    print("Screen geometry: {0}".format(s.availableGeometry()))
for s in QApplication.primaryScreen().virtualSiblings():
    print("Screen geometry: {0}".format(s.availableGeometry()))

window = SelectorWindow()
window.show()
app.exec_()
sys.exit(0)
print("== Read in ==")
    
