#!/bin/sh -x

uvicorn kookaburra.main:app ${@}
