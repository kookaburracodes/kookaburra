#!/bin/sh -e

npx tailwindcss -m -i ./static/css/input.css -o ./static/css/tailwind.css ${@} # --watch
