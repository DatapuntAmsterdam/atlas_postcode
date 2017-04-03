FROM amsterdam/docker_python:latest
MAINTAINER datapunt.ois@amsterdam.nl

WORKDIR /app
EXPOSE 8080

COPY requirements.txt /app/
RUN pip install uwsgi \
 && pip install -r requirements.txt \
 && adduser --system postcode

COPY . /app/
RUN chmod 755 /app/docker-run.sh

USER postcode

CMD ["/app/docker-run.sh"]
