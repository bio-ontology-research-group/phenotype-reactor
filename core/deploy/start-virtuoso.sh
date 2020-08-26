#!/bin/bash
if [ "$1" == "" ];
then
echo "ERROR: container id is required argument"
fi

cd ../support/virtuoso
if [ ! "$(docker ps -q -f name=$1)" ]; then
    if [ "$(docker ps -aq -f status=exited -f name=$1)" ]; then
        # cleanup
        echo "cleaned up virtuoso container"
        docker stop $1
        docker rm $1
    fi
    # run your container
    echo "running virtuoso container"
    docker-compose up -d
    sleep 15;

elif [ "$(docker ps -q -f name=$1)" ]; then
    echo "Virtuoso container already running"
fi