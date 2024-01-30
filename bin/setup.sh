#!/bin/sh

ROOT=$(dirname "$0" | xargs dirname)
source $ROOT/conf

APP="sh-cgi"
PORT=8080

echo "Stopping old container.." >&2
docker stop $APP
echo "done" >&2

echo "Removing old container.." >&2
docker rm $APP
echo "done" >&2

echo "Building new container.." >&2
docker build -t $APP .
echo "done" >&2

echo "Running new container.." >&2
docker run \
	-d \
	--name=$APP \
	-p $PORT:80 \
	-v $(pwd)/cgi-bin:/usr/local/apache2/cgi-bin \
	$APP
echo "done" >&2
