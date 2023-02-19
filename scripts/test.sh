#!/bin/sh -ex

./scripts/lint.sh

# TODO: get to 💯
# pytest --cov=kookaburra --cov=tests --cov-report=term-missing --cov-report=xml -o console_output_style=progress --disable-warnings --cov-fail-under=100 ${@}
pytest --cov=kookaburra --cov=tests --cov-report=term-missing --cov-report=xml -o console_output_style=progress --disable-warnings ${@}
