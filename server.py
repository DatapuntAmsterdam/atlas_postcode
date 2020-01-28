import logging
import os
import re
import sys

import psycopg2
from flask import Flask, request, redirect, render_template

log = logging.Logger(__name__)
log.addHandler(logging.StreamHandler(stream=sys.stdout))
log.setLevel(logging.INFO)

log.info("Starting %s application", __name__)


def get_docker_host():
    """
    Looks for the DOCKER_HOST environment variable to find the VM
    running docker-machine.

    If the environment variable is not found, it is assumed that
    you're running docker on localhost.
    """
    d_host = os.getenv('DOCKER_HOST', None)
    if d_host:
        if re.match(r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$', d_host):
            return d_host

        return re.match(r'tcp://(.*?):\d+', d_host).group(1)
    return 'localhost'


app = Flask(__name__)

db_host = os.environ.get('DATABASE_PORT_5432_TCP_ADDR', get_docker_host())
db_port = os.environ.get('DATABASE_PORT_5432_TCP_PORT', 5432)
db_user = os.environ.get('DB_USER', 'bag')
db_name = os.environ.get('DB_NAME', 'bag')
db_pass = os.environ.get('DB_PASS', 'insecure')

connection_str = ("dbname='{}' user='{}' host='{}' password='{}' port='{}'"
                  .format(db_name, db_user, db_host, db_pass, db_port))

log.debug("Connecting to %s", connection_str)


@app.route("/")
def handler():
    postcode = request.args.get('p', None)
    huisnummer = request.args.get('h', None)
    huisletter = request.args.get('hl', None)
    huisnummer_toevoeging = request.args.get('ht', None)

    if not postcode:
        return "Parameter `p` (postcode) is verplicht", 400

    if not huisnummer:
        return "Parameter `h` (huisnummer) is verplicht", 400

    postcode = postcode.replace(' ', '').upper()
    huisnummer = int(huisnummer)

    if huisnummer_toevoeging:
        huisnummer_toevoeging = huisnummer_toevoeging.upper()

    if huisletter:
        huisletter = huisletter.upper()

    vbo_id = get_vbo_id(
        postcode=postcode,
        huisnummer=huisnummer,
        huisletter=huisletter,
        huisnummer_toevoeging=huisnummer_toevoeging)

    if not vbo_id:
        return render_template(
            "not_found.html",
            postcode=postcode,
            huisnummer=huisnummer,
            huisletter=huisletter,
            huisnummer_toevoeging=huisnummer_toevoeging
        ), 404

    return redirect(
        "https://data.amsterdam.nl/data/bag/verblijfsobject/id{}/".format(
            vbo_id))


@app.route("/status/health")
def health():
    try:
        get_vbo_id('1061VB', 113, None, None)
    except Exception:
        log.exception("Could not obtain data")
        raise

    return "OK"


def get_vbo_id(postcode, huisnummer, huisletter, huisnummer_toevoeging):
    params = dict(
            postcode=postcode,
            huisnummer=huisnummer,
            huisletter=huisletter,
            huisnummer_toevoeging=huisnummer_toevoeging,
    )

    query = """SELECT num.verblijfsobject_id
               FROM bag_nummeraanduiding num
               WHERE num.postcode = %(postcode)s
               AND num.huisnummer = %(huisnummer)s """

    if huisletter:
        query += " AND num.huisletter = %(huisletter)s "

    if huisnummer_toevoeging:
        query += " AND num.huisnummer_toevoeging = %(huisnummer_toevoeging)s "

    log.debug("Executing query %s with params %s", query, params)

    with psycopg2.connect(connection_str) as conn:
        with conn.cursor() as cur:
            cur.execute(query, params)
            rows = cur.fetchall()
            if rows:
                return rows[0][0]

    return None


if __name__ == "__main__":
    app.run(debug=True)
