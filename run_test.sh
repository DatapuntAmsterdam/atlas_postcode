#!/usr/bin/env bash
docker exec $(docker-compose ps -q database) update-atlas.sh

curl -vs "http://localhost:9090/?p=1079WJ&h=128&hl=h" 2>&1 | grep -q "Location: https://atlas.amsterdam.nl/#/?zoek=1079WJ%20128%20h" ; echo $?
