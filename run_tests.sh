#!/bin/bash

set -e

root_path=$(dirname $(realpath $0))
$root_path/pytest_runner.sh "$@"
