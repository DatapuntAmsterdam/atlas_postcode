FROM python:3
MAINTAINER datapunt@amsterdam.nl

WORKDIR /app
EXPOSE 8080

RUN pip install uwsgi

COPY . /app/
RUN pip install -r requirements.txt \
 && chmod 755 /app/run_test.sh

RUN adduser --system postcode
USER postcode

CMD uwsgi --ini /app/uwsgi.ini
