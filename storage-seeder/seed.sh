#!/bin/bash

LIMIT=10000

SYSTEMS=(Windows Linux Android iOS macOS)
COUNTRIES=(Serbia Germany Spain Portugal Netherlands)
BROWSERS=(Chrome Firefox Opera)
IPS=(173.64.191.52 9.61.48.62 23.209.243.87 107.251.232.210 73.208.64.149 176.54.5.251 73.208.64.149)

RANDOM=$$$(date +%s)

i=0
while [[ ${i} -lt LIMIT ]]; do
    ip=${IPS[$RANDOM % ${#IPS[@]}]}
    country=${COUNTRIES[$RANDOM % ${#COUNTRIES[@]}]}
    system=${SYSTEMS[$RANDOM % ${#SYSTEMS[@]}]}
    browser=${BROWSERS[$RANDOM % ${#BROWSERS[@]}]}
    ts=`date +"%Y-%m-%d %H:%M:%S"`
    i=$((i+1))
    if [[ $((i % 50)) == 0 ]]; then
        echo "Inserted ${i}/${LIMIT} rows"
    fi
    mysql --host=storage --port=3306 -u root -ppassword -e "insert into visitorsdb.visits values ('${ip}', '${country}', '${system}', '${browser}', '${ts}');" 2> /dev/null
    sleep $((RANDOM % 3 + 1))
done
