#!/bin/sh -e

POSTGRES_DB=${POSTGRES_DB:-kookaburra}

# run postgres in a docker container
echo "Starting postgres in a docker container."
docker run --rm -d --name kookaburra-postgres \
-p 5432:5432 \
-e POSTGRES_PASSWORD=kookaburra \
-e POSTGRES_USER=kookaburra \
-e POSTGRES_PASSWORD=kookaburra \
-e POSTGRES_DB=$POSTGRES_DB \
postgres:15.1

echo "Creating another database called kookaburra_test for testing."
sleep 1
if [ -t 1 ] ;
then
    docker exec -it kookaburra-postgres psql -h 0.0.0.0 -U kookaburra -c "CREATE DATABASE kookaburra_test;"
else
    echo "not a terminal";
fi
