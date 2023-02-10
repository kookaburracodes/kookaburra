#!/bin/sh -ex

mypy kookaburra tests
black kookaburra tests --check
ruff kookaburra tests scripts
