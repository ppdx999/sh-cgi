#!/bin/sh

docker exec -t sh-cgi  sh -c 'chmod +x /usr/local/apache2/cgi-bin/*.cgi'
