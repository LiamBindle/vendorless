#!/bin/sh
set -x

echo $@
if [ -z "$(ls -A /package)" ]; then
    # packages is empty

    # set up dummy poetry project for the environment
    mkdir -p /package
    cd /package
    poetry init --no-interaction
    while [ "${1#vendorless.}" != "$1" ]; do
        poetry add "$1"
        shift
    done
    poetry install --no-root
    which mkdocs 
else
    cd /package
    poetry install
fi

poetry run vl "$@"