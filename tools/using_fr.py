import cv2
#import vdms
import sys
import os
from os.path import join,isdir,exists,basename
import urllib
import time
import json
import unittest
import numpy as np
import csv
import face_recognition

import glob

def get_descriptors(imagePath , outputPath,blob_array):

    print(f"Reading {imagePath}")
    image = cv2.imread(imagePath)
    try:
        print(f"{image.shape}")
        x_scale = 1.0
        y_scale = 1.0
        (h,w,dim) = image.shape
        if h > 500 or w > 500:
            if h > 1000 or w > 1000:
                x_scale = y_scale = 0.6
            else:
                x_scale = y_scale = 0.8
        #if x_scale < 1.0 or y_scale < 1.0:
        #    image = cv2.resize(image, (0,0), fx=x_scale,fy=y_scale)
    except Exception:
        if image is None:
            print(f"failed to load {imagePath} ( no image )")
        else:
            print(f"failed to resize {image.shape()}")
        return

    rgb   = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    boxes = face_recognition.face_locations(rgb, model="hog")

    # compute the facial embedding for the face
    encodings = face_recognition.face_encodings(rgb, boxes)

    # Draw a rectangle around the faces
    counter = 0
    for (top, right, bottom, left) in boxes:
        cv2.rectangle(image, (left, top), (right, bottom), (0, 255, 0), 2)
        y = top - 15 if top - 15 > 15 else top + 15
        cv2.putText(image, str(counter), (left, y), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (0, 255, 0), 2)
        counter += 1

    input_name = basename( imagePath )
    output_path =join( outputPath,f"{input_name[:-4]}.jpg") 
    print(f"Outputting to {output_path}")
    cv2.imwrite(output_path, image)
    #from IPython.display import Image
   # display(Image("save.jpg"))

    # print (len(encodings))
    # print (len(encodings[0]))
    # print (encodings[0])


    for ele in encodings:
        blob_array.append(np.array(ele).astype('float32').tobytes())

    #return blob_array

if __name__ == "__main__":
  base = sys.argv[1]
  outbase = "feature_vectors"
  print(f"processing from {base} using dir_??? glob")
  blob_array = []
  for globbed in glob.glob( join( base , "dir_???")):
      print(f"* {globbed}")
      if isdir( globbed ):
          for celeb_dir in os.listdir( globbed ):
            print(f" ** {celeb_dir}")
            out_celeb_dir = join(outbase, celeb_dir.replace(" ","_"))
            print(f" ++ out {out_celeb_dir}")
            if not exists( out_celeb_dir ):
                os.mkdir(out_celeb_dir)
            celeb_image_dir = join( globbed, celeb_dir )
            for image in os.listdir( celeb_image_dir ):
                print(f" ** {image}")
                image_path = join( celeb_image_dir, image )
                get_descriptors(image_path,out_celeb_dir,blob_array)
            sys.exit(0)
  fp = open( join(outbase,"features.npy"),'wb')
  fp.write(blob_array)
  fp.close()
