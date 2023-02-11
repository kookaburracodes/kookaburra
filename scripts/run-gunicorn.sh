#!/bin/sh -x

gunicorn kookaburra.main:app -c kookaburra/gunicorn_conf.py ${@}
