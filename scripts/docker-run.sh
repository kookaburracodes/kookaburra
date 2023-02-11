#!/bin/sh -x

IMAGE_VERSION=${IMAGE_VERSION:=latest}
docker run \
--interactive \
--tty \
--env-file=".env.local" \
--publish="8000:8000" \
"gcr.io/kookaburra-codes-dev/kookaburra:${IMAGE_VERSION}"
