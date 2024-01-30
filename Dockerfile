FROM httpd

COPY httpd.conf /usr/local/apache2/conf/httpd.conf
COPY api/* /usr/local/apache2/api/
COPY public/* /usr/local/apache2/public/
COPY bin/* /usr/local/apache2/bin/
