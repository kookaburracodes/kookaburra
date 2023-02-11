#!/bin/sh -x

IMAGE_VERSION=${IMAGE_VERSION:=latest}
docker build \
--platform linux/amd64 \
--tag "gcr.io/kookaburra-codes-dev/kookaburra:${IMAGE_VERSION}" .
