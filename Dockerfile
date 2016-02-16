FROM nginx:latest
MAINTAINER datapunt@amsterdam.nl

EXPOSE 80

COPY default.conf /etc/nginx/conf.d/
COPY run_test.sh /usr/local/bin/
RUN chmod 700 /usr/local/bin/run_test.sh