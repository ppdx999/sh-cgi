FROM httpd

RUN sed -e 's/#LoadModule cgid_module/LoadModule cgid_module/' \
		-e 's/#LoadModule cgi_module/LoadModule cgi_module/' \
		-i /usr/local/apache2/conf/httpd.conf

COPY bin/* /usr/local/apache2/bin/
