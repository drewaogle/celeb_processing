#!/bin/bash

# Process sequentially
BASE_DIR=..
OF_DIR=$(realpath ../build_openface/bin)
for part_dir in $(ls -d $BASE_DIR/dir_???);
do
	echo Processing $part_dir
	OIFS=$IFS
	IFS=$(echo -en "\n\n")
	#ALL=$(ls ${part_dir})
	for celeb_dir in ${part_dir}/*;
	do
		name=$(basename "$celeb_dir")
		no_space=$(echo $name|sed -re 's: :_:g')
		echo "[$celeb_dir] $name => $no_space" # => $no_space"
		absolute_celeb_dir=$(realpath "$celeb_dir")
		if [ ! -e "$no_space" ];then
			mkdir "$no_space"
			cd "$no_space"
			find "${absolute_celeb_dir}" -type f -print0 | xargs -0 printf -- '-f\0%s\0' | xargs -0 $OF_DIR/FaceLandmarkImg > run_log
			ret=$?
			echo "Return was $ret"
			cd ".."
		else
			echo "$no_space exists, skipping."
		fi
	done
		IFS=$OIFS
done
