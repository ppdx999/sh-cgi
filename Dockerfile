FROM httpd

COPY httpd.conf /usr/local/apache2/conf/httpd.conf
COPY public/* /usr/local/apache2/public/
COPY bin/* /usr/local/apache2/bin/
