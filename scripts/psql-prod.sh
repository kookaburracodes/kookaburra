#!/bin/sh -e

PGPASSWORD=${PGPASSWORD} psql -d kookaburra-dev -U kookaburra -h 0.0.0.0 -p 5432 "${@}"
