#!/bin/sh -ex

./scripts/lint.sh

pytest --cov=kookaburra --cov=tests --cov-report=term-missing --cov-report=xml --cov-report=html -o console_output_style=progress --disable-warnings --cov-fail-under=100 --asyncio-mode=auto ${@}
