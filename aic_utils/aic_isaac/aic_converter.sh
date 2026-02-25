#!/bin/bash

set -e

SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )

DOCKER_DIR_PATH=$SCRIPT_DIR/../../docker

cd $DOCKER_DIR_PATH


# This is a flag to build entire converter
BUILD_TARGET=kilted_stage docker compose build converter

docker cp $(docker create --rm ghcr.io/intrinsic-dev/aic/aic_converter):/tmp/aic.sdf ./aic.sdf

# Display help function
# function display_help {

# }
