#!/bin/sh -e

echo "setting ENV_PROD_FILE"
gh secret set ENV_PROD_FILE --app actions --repos kookaburracodes/kookaburra --body $(base64 -i .env.prod | tr -d '\n')

echo "setting KB_PEM_FILE"
gh secret set KB_PEM_FILE --app actions --repos kookaburracodes/kookaburra --body $(base64 -i kookaburra-codes.2023-02-17.private-key.pem | tr -d '\n')
