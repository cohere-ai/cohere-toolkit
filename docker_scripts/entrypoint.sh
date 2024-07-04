#!/bin/bash
set -e

# shellcheck source=runtime/functions
source "${PG_APP_HOME}/functions"

[[ ${DEBUG} == true ]] && set -x

# allow arguments to be passed to postgres
if [[ ${1:0:1} = '-' ]]; then
  EXTRA_ARGS="$@"
  set --
elif [[ ${1} == postgres || ${1} == $(command -v postgres) ]]; then
  EXTRA_ARGS="${@:2}"
  set --
fi

# default behaviour is to launch postgres
if [[ -z ${1} ]]; then
  map_uidgid

  create_datadir
  create_certdir
  create_logdir
  create_rundir
  set_resolvconf_perms
  configure_postgresql

  run_postgre
  run_frontend
  run_terrarium
  run_backend_poetry

else
  exec "$@"
fi
