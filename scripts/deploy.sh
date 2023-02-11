#!/bin/sh -e

./scripts/docker-build.sh

./scripts/docker-push.sh

./scripts/gcloud-beta-run-deploy.sh
