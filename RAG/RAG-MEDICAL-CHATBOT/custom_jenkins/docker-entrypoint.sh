#!/bin/sh
set -eu

unset http_proxy https_proxy HTTP_PROXY HTTPS_PROXY all_proxy ALL_PROXY no_proxy NO_PROXY

# The container runs as jenkins; avoid root-only writes under /etc here.
git config --global --unset-all http.proxy || true
git config --global --unset-all https.proxy || true

exec /usr/bin/tini -- /usr/local/bin/jenkins.sh "$@"