#!/bin/env python3

import os,sys
from os.path import isdir,exists,join,splitext,basename
from shutil import copyfile

range_bottom=1
range_top=25
def process( input_dir, output_dir ):
    if not isdir( input_dir ):
        print(f"Bad input dir: {input_dir}")
        sys.exit(1)
    if not isdir( output_dir ):
        try:
            os.mkdir( output_dir )
        except:
            print(f"Failed to create output directory: {output_dir}")
            sys.exit(1)
    print("Input and output set")
    for root, dirs,files in os.walk( input_dir ):
        for name in files:
            fileroot,ext = splitext(name)
            if not ext == ".jpg":
                continue
            if int(fileroot) in range(range_bottom,range_top):
                #print("File:" + join(root,name))
                filedir = basename(root)
                print(f"Copy {name} to {output_dir}/{filedir}")
                output_file_dir = join(output_dir,filedir )
                if not isdir( output_file_dir ):
                    try:
                        os.makedirs( output_file_dir)
                    except:
                        print(f"Failed to make output directory {output_file_dir}")
                        sys.exit(1)
                output_path = join(output_file_dir,name)
                if not exists( output_path):
                    copyfile( join(root,name), output_path )
        #for name in dirs:
        #    print("Dir:" + join(root,name))
    print("Subset created")
    sys.exit(1)

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print("missing args")
        sys.exit(1)
    process( sys.argv[1], sys.argv[2])
