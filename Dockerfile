FROM nginx:latest
MAINTAINER datapunt@amsterdam.nl

EXPOSE 80

COPY default.conf /etc/nginx/conf.d/

#CMD /app/docker-entrypoint.sh