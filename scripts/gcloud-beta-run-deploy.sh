#!/bin/sh -e

VARS=$(python -c "print(','.join([line.strip() for line in open('.env.prod').readlines()]))")

gcloud beta run deploy kookaburra-mvp \
--image gcr.io/kookaburra-codes-dev/kookaburra:latest \
--region us-central1 \
--platform managed \
--allow-unauthenticated \
--set-env-vars $VARS \
--no-cpu-throttling \
--project kookaburra-codes-dev \
--port 8000
