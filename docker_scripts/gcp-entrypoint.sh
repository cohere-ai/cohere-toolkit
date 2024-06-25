#!/bin/bash
set -e

# shellcheck source=runtime/functions
source "${PG_APP_HOME}/functions"

[[ ${DEBUG} == true ]] && set -x

# default behaviour is to launch apps
if [[ -z ${1} ]]; then
  run_nginx
  run_frontend_proxy
  run_terrarium
  run_backend_poetry
else
  exec "$@"
fi
