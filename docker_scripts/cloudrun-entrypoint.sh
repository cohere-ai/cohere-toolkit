#!/bin/bash
set -e

# shellcheck source=runtime/functions
source "${APP_HOME}/functions"

[[ ${DEBUG} == true ]] && set -x

# default behaviour is to launch postgres
if [[ -z ${1} ]]; then
  run_frontend_cloud_run
  run_backend

else
  exec "$@"
fi
