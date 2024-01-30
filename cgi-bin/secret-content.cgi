#!/bin/sh

session-check "${HTTP_COOKIE:-}"

if [ $? -ne 0 ]; then
		echo "Content-Type: text/html"
		echo
		echo "You are not logged in"
		exit 0
fi

cat <<-HTTP_RESPONSE
Content-Type: text/html
charset: UTF-8

This is a secret content
HTTP_RESPONSE
