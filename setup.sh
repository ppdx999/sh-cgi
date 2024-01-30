#!/bin/sh

chmod +x $(dirname "$0")/bin/*
chmod +x $(dirname "$0")/public/*.sh

source $(dirname "$0")/conf

echo "Stopping old container.." >&2
docker stop $APP
echo "done" >&2

echo "Removing old container.." >&2
docker rm $APP
echo "done" >&2

echo "Removing old image.." >&2
docker rmi $APP
echo "done" >&2

echo "Building new container.." >&2
docker build -t $APP .
echo "done" >&2

echo "Running new container.." >&2
docker run \
	-d \
	--name=$APP \
	-p $PORT:80 \
	-v $(pwd)/api:/usr/local/apache2/api \
	-v $(pwd)/public:/usr/local/apache2/public \
	$APP
echo "done" >&2
