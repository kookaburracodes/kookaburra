#!/bin/sh -e

#
#   To install cloud_sql_proxy follow these instructions https://github.com/GoogleCloudPlatform/cloud-sql-proxy#installation
#   And then:
#       chmod +x cloud_sql_proxy
#       mv cloud_sql_proxy /usr/local/bin
#
cloud_sql_proxy kookaburra-codes-dev:us-central1:kb-dev --port 5432 &
cloud_sql_proxy_pid=$!

echo ""
echo "You can now connect to the database using the following command in another session:"
echo "./scripts/psql-prod.sh -c \"select count(*) from users where created_at > DATE(CURRENT_DATE);\""
echo "Press Ctrl+C to stop this process."
echo ""

wait $cloud_sql_proxy_pid
