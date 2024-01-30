#!/bin/sh

source $(dirname "$0")/conf

docker exec -t $APP  sh -c 'chmod +x /usr/local/apache2/cgi-bin/*.cgi'
