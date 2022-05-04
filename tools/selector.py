#!/usr/bin/env python3

import sys
from os import listdir
from os.path import isfile,join
from PyQt5.QtWidgets import QApplication,QLabel,QVBoxLayout,QHBoxLayout,QWidget
from PyQt5.QtGui import QPixmap

app = QApplication([])
window = QWidget()

mainvbox = QVBoxLayout()
imagecomparebox = QHBoxLayout()
facebox = QVBoxLayout()

outputlabel = QLabel()
facelabels = []
statuslabel = QLabel("Status Layout")
imagecomparebox.addWidget(outputlabel)
imagecomparebox.addLayout(facebox)
mainvbox.addWidget(statuslabel)
mainvbox.addLayout(imagecomparebox)
window.setLayout(mainvbox)




def run_ui():
    # top center is celeb name
    # left side is source image
    # right side is list of faces
    label = QLabel('Hello ApertureData')
    label.show()


# for directory
for element in listdir("."):
    element_path = join(".",element)
    if not isfile( element_path ):
        print(f"- Processing {element} as {element_path}")
        element_path = join( element_path , "processed" )
        for celeb_element in listdir(element_path):
            celeb_element_path = join(element_path,celeb_element)
            #if celeb_element[-4:] == ".jpg":
            if isfile(celeb_element_path) and celeb_element[-4:] == ".jpg":
                face_dir = "{0}_aligned".format( celeb_element[:-4] )
                face_dir_path = join( element_path, face_dir )
                face_count = len( [ f for f in listdir( face_dir_path ) if isfile( join( face_dir_path, f )) ] )
                face_plural = "faces" if face_count != 1 else "face"
                outputlabel.setPixmap(QPixmap( celeb_element_path))
                [ facelabel.hide() for facelabel in facelabels ]
                fnum =0
                for fimg in listdir( face_dir_path ):
                    fnum = fnum + 1
                    if len( facelabels ) < fnum :
                        l = QLabel()
                        facebox.addWidget(l)
                        facelabels.append(l)
                    facelabels[fnum-1].setPixmap( QPixmap( join( face_dir_path, fimg )))
                    facelabels[fnum-1].show()
                #mainvbox.show()
                statuslabel.show()
                outputlabel.show()
                statuslabel.setText(f"Celeb: {element_path}, Image: {celeb_element[:-4]}")
                window.show()


                app.exec_()
                sys.exit(0)
                #print(f"  + Processing file {celeb_element} and face dir {face_dir} with {face_count} {face_plural}")
            #else:
            #    print(f"Ignored {celeb_element} and {celeb_element[-4:]}")
        #break;
print("== Read in ==")
    
