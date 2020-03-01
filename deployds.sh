#!/bin/bash
if [ "$1" == "" ];
then
echo "ERROR: container id is required argument"
fi

if [ "$2" == "" ];
then
echo "ERROR: data directory is required argument"
fi


echo "Downloading phenotype data ..."
curl -L 'http://phenomebrowser.net/archive/latest' --output phenotype-data.tar.gz


echo "Extracting phenotype data ..."
tar -xvf phenotype-data.tar.gz
rm -rf phenotype-data.tar.gz

cd data-*

echo "Copying phenotype-reactor data to virtuoso docker container for loading"
#delete existing data folder in container
docker exec $1 rm -rf /usr/share/proj
#create directory
docker exec $1 mkdir -p /usr/share/proj
#copy files from source directory
docker cp . "$1":/usr/share/proj
echo "completed copying"

rm -rf data-*
echo "cleaned extracted data"