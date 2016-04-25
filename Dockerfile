FROM python:3
MAINTAINER datapunt.ois@amsterdam.nl

WORKDIR /app
EXPOSE 8080

COPY requirements.txt /app/
RUN pip install uwsgi \
 && pip install -r requirements.txt \
 && adduser --system postcode

COPY . /app/
RUN chmod 755 /app/run_test.sh

USER postcode

CMD uwsgi --ini /app/uwsgi.ini
