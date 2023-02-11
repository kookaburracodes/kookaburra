#!/bin/sh -e

base64 -i .env.prod | tr -d '\n' > .env.prod.base64
