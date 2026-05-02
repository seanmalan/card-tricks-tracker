#!/bin/sh
# Fix ownership of the bind-mounted data directory (which Docker creates as
# root by default) so the unprivileged 'app' user can read and write it,
# then drop privileges and exec the app.
set -e

DATA_DIR="${DATA_DIR:-/data}"
mkdir -p "$DATA_DIR"

if [ "$(id -u)" = "0" ]; then
  chown -R app:app "$DATA_DIR"
  exec gosu app "$@"
fi

exec "$@"
