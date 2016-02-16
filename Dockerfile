FROM nginx:latest
MAINTAINER datapunt@amsterdam.nl

EXPOSE 80

COPY default.conf /etc/nginx/conf.d/