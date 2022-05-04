#!/usr/bin/env python3

import sys
from os import listdir
from os.path import isfile,join,exists,basename
from PyQt5.QtWidgets import QApplication,QLabel,QVBoxLayout,QHBoxLayout,QWidget
from PyQt5.QtGui import QPixmap
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




class SelectorWindow(QWidget):
    def __init__(self):
        super(SelectorWindow,self).__init__()
        self.selection = FacePathGeneration(".")
        self.mainvbox = QVBoxLayout()
        self.imagecomparebox = QHBoxLayout()
        self.facebox = QVBoxLayout()

        self.outputlabel = QLabel()
        self.facelabels = []
        self.statuslabel = QLabel("Status Layout")
        self.imagecomparebox.addWidget(self.outputlabel)
        self.imagecomparebox.addLayout(self.facebox)
        self.mainvbox.addWidget(self.statuslabel)
        self.mainvbox.addLayout(self.imagecomparebox)
        self.setLayout(self.mainvbox)
        self.setup( *next(self.selection))
        self.show()
    def setup( self, element, celeb_element_path,face_dir_path ):
        face_count = len( [ f for f in listdir( face_dir_path ) if isfile( join( face_dir_path, f )) ] )
        face_plural = "faces" if face_count != 1 else "face"
        self.outputlabel.setPixmap(QPixmap( celeb_element_path))
        [ facelabel.hide() for facelabel in self.facelabels ]
        fnum =0
        for fimg in listdir( face_dir_path ):
            fnum = fnum + 1
            if len( self.facelabels ) < fnum :
                l = QLabel()
                self.facebox.addWidget(l)
                self.facelabels.append(l)
            self.facelabels[fnum-1].setPixmap( QPixmap( join( face_dir_path, fimg )))
            self.facelabels[fnum-1].show()
        #mainvbox.show()
        self.statuslabel.show()
        self.outputlabel.show()

        celeb_picture_number = basename(celeb_element_path)[:-4]

        self.statuslabel.setText(f"Celeb: {element}, Image: {celeb_picture_number}")


    def keyPressEvent(self,event):
        if event.key() == Qt.Key_Q:
            print("Exiting")
            self.deleteLater()
            sys.exit(1)
        elif event.key() == Qt.Key_X:
            print("Deselecting All")
        elif event.key() == Qt.Key_1:
            print("Selecting Item 1")
        elif event.key() == Qt.Key_Space:
            print("Selecting Current Item")
        elif event.key() == Qt.Key_Enter:
            print("Accepting")


app = QApplication([])
window = SelectorWindow()
window.show()

def run_ui():
    # top center is celeb name
    # left side is source image
    # right side is list of faces
    label = QLabel('Hello ApertureData')
    label.show()


app.exec_()
sys.exit(0)
print("== Read in ==")
    
