#!/bin/bash
if [ "$(id -u)" != "0" ]; then
  echo "Error: Run this script as root.  Try:" 1>&2
  echo "sudo" $0 $@ 1>&2
  exit 1
fi

docker build -no-cache -rm=true .
if [ $? != 0 ]; then
  echo "Error: docker build command failed."
  exit 1
fi
OUT=$(docker ps -a)
IMAGE=$(docker images)
ID=$(echo $OUT | cut -d \  -f 9)
IMID=$(echo $IMAGE | cut -d \  -f 10)
echo "Image ID is " $IMID
echo "Tagging" $ID
docker tag -f $IMID "tekgek/praxyk:latest"
