#!/bin/sh

echo "Content-Type: text/html"
echo ""
echo "Your sh server work well"

echo "this is query string"
echo "$QUERY_STRING"

echo "this is request method"
echo "$REQUEST_METHOD"

echo "this is request body"

dd bs=$CONTENT_LENGTH | cgi-name
