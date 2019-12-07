#!/usr/bin/env bash

# Run either the ui or kernel depending on the value specified
# in the CAULDRON_CONTAINER_TYPE environment variables, which
# is set in the container image at build time via a build arg.
python "/launch/${CAULDRON_CONTAINER_TYPE}-run.py" "$@"
