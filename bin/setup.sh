#!/bin/sh

app_name="sh-cgi"
port=8080

echo "Stopping old container.." >&2
docker stop $app_name
echo "done" >&2

echo "Removing old container.." >&2
docker rm $app_name
echo "done" >&2

echo "Building new container.." >&2
docker build -t $app_name .
echo "done" >&2

echo "Running new container.." >&2
docker run \
	-d \
	--name=$app_name \
	-p $port:80 \
	-v $(pwd)/cgi-bin:/usr/local/apache2/cgi-bin \
	$app_name
echo "done" >&2
