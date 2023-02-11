#!/bin/sh -e

IMAGE_VERSION=${IMAGE_VERSION:=latest}
docker push "gcr.io/kookaburra-codes-dev/kookaburra:${IMAGE_VERSION}"
