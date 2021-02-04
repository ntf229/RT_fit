#!/bin/bash

# to run, use "bash sph.sh"
# to run with no dust, use "bash sph.sh -nodust"

name_default="sph_face_nodust"

while getopts "n:d" opt
do
   case "$opt" in
      n ) name="$OPTARG" ;;
      d ) dust="True" ;;
   esac
done

if [ -z ${name+x} ]; then name="$name_default"; else echo "name is set to '$name$'"; fi

echo name is "$name"

if [ $dust == "True" ]; then
  echo "Including dust"
else
  echo "No dust"
fi

