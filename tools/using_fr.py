#!/usr/bin/env python3
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
import io

import glob

from aperturedb import Utils, Connector

from sqlitedict import SqliteDict

mydict = SqliteDict('./processed.sqlite', autocommit=True)
for key, value in mydict.items():
    print(key, value)
print(len(mydict))




user = "admin"
password = "admin"

con = Connector.Connector(user=user, password=password, port=55557)
#utils = Utils.Utils(con)
#utils.remove_descriptorset(search_set_name)
#utils.add_descriptorset(search_set_name, 512, metric="L2", engine="FaissFlat")

errors = 0

search_set_name = "celebs"

def get_descriptors(name,imagePath , outputPath,blob_array):

    input_name = basename( imagePath )
    number = input_name[:-4]
    processed_key = f"{name}__{number}" 
    if processed_key in mydict:
        return
    print(f"Reading {imagePath}")
    image = cv2.imread(imagePath)
    fd = open(imagePath, 'rb')
    rawImage = fd.read()
    fd.close()
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
        if x_scale < 1.0 or y_scale < 1.0:
            image = cv2.resize(image, (0,0), fx=x_scale,fy=y_scale)
    except Exception:
        if image is None:
            print(f"failed to load {imagePath} ( no image )")
        else:
            print(f"failed to resize {image.shape()}")
        return

    ok, jpg_cv2 = cv2.imencode( ".jpg",image)
    jpg_buffer = io.BytesIO(jpg_cv2).getvalue()
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

    output_path =join( outputPath,f"{input_name[:-4]}.jpg") 
    print(f"Outputting to {output_path}")
    cv2.imwrite(output_path, image)
    #from IPython.display import Image
   # display(Image("save.jpg"))

    # print (len(encodings))
    # print (len(encodings[0]))
    # print (encodings[0])

    #ignore image if no boxes.
    if len(boxes) == 0 :
       return
    (top,right,bottom,left) = boxes[0]
    t = [
            {
                "AddImage": {
                    "_ref": 1,
                    "properties": {
                        "celeb": name,
                        "celeb_id": "{}_{}".format(name.replace(' ','_'),number),
                        "class" : "celeb"
                        },
                    }
                }, {
                    "AddBoundingBox": {
                        "_ref": 2,
                        "image": 1,
                        "rectangle": {
                            "x": top,
                            "y": left,
                            "width": right - left,
                            "height": bottom - top
                            }
                        }
                    }, {
                        "AddDescriptor": {
                            "set": search_set_name,
                            "connect": {
                                "ref": 1
                                }
                            }
                        }

                    ]

    float_array = np.array(encodings[0]).astype('float32')
    array_len = len(float_array)
    #print("Encodings: {}".format(len(encodings)))
    print("Array: {}".format(len(float_array)))
    keypoints = f"{array_len}"
    for encoding_float in float_array:
        keypoints = f"{keypoints} {encoding_float}"

    #print(f"{keypoints}")

#   # t[0]["AddImage"]["properties"]["keypoints"] = f"10 {p['lefteye_x']} {p['lefteye_y']} {p['righteye_x']} {p['righteye_y']} {p['nose_x']} {p['nose_y']} {p['leftmouth_x']} {p['leftmouth_y']} {p['rightmouth_x']} {p['rightmouth_y']}"
    #t[0]["AddImage"]["properties"]["keypoints"] = keypoints
    (res,blo) = con.query(t,[jpg_buffer,float_array.tobytes()])
    if isinstance(res,dict) and res['status'] < 0:
        print("{}".format(res))
        sys.exit(0)
    print("{}".format(res))
    mydict[processed_key] = True



    #return blob_array
TEST_SINGLE=False
if __name__ == "__main__":
  base = sys.argv[1]
  outbase = "feature_vectors"
  print(f"processing from {base} using dir_??? glob")
  if not "_descriptor_set" in mydict:
    query = [{
            "AddDescriptorSet": {
                "name":       search_set_name,
                "dimensions": 128
            }
        }]
    (res,blo) = con.query(query)
    print("{}".format(res))
    if "status" in res and res['status'] < 0:
        print("{}".format(res))
        sys.exit(0)
    if "status" in res[0]["AddDescriptorSet"] and res[0]["AddDescriptorSet"]["status"] < 0:
        print("{}".format(res))
        sys.exit(0)
    mydict["_descriptor_set"] = True

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
            for image_number in range(1,20): #os.listdir( celeb_image_dir ):
                image = f"{image_number}.jpg"
                image_path = join( celeb_image_dir, image )
                if not exists( image_path ):
                    continue
                print(f" ** {image}")
                get_descriptors(celeb_dir,image_path,out_celeb_dir,blob_array)
            if TEST_SINGLE:
                sys.exit(0)
  #fp = open( join(outbase,"features.npy"),'wb')
  #fp.write(blob_array)
  #fp.close()
  mydict.close()
