#!/bin/bash

ME=$(basename "$0")

FULLCHAIN="/etc/letsencrypt/live/$IDA_DOMAIN_NAME/fullchain.pem"
PRIVKEY="/etc/letsencrypt/live/$IDA_DOMAIN_NAME/privkey.pem"

while [ ! -f "$FULLCHAIN" ]; do sleep 1; done
while [ ! -f "$PRIVKEY" ]; do sleep 1; done

echo >&3 "$ME: info: Found fullchain and privkey."

exit 0
