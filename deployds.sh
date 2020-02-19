#!/bin/bash
if [ "$1" == "" ];
then
echo "ERROR: container id is required argument"
fi

if [ "$2" == "" ];
then
echo "ERROR: data directory is required argument"
fi


echo "Copying phenotype-reactor data to virtuoso docker container for loading"
docker exec $1 mkdir -p /usr/share/proj
docker cp $2/. "$1":/usr/share/proj
echo "completed copying"
