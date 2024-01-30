#!/bin/sh

ROOT=$(dirname "$0" | xargs dirname)
source $ROOT/conf

docker exec -t $APP  sh -c 'chmod +x /usr/local/apache2/cgi-bin/*.cgi'
