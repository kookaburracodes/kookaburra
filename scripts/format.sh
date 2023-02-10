#!/bin/sh -ex

black kookaburra tests scripts
ruff kookaburra tests scripts --fix
