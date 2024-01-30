#!/bin/sh

# Login check
is_login="no"
session-check "${HTTP_COOKIE:-}"
case $? in 0) is_login="yes";; esac

status="Logout"
case $IS_LOGIN in "yes") status="Login";; *) status="Logout";; esac

echo "Content-Type: text/html"
echo ""
cat index.template.html | sed -e "s/@@STATUS@@/$status/g"
