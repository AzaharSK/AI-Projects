#!/bin/sh
set -eu

unset http_proxy https_proxy HTTP_PROXY HTTPS_PROXY all_proxy ALL_PROXY no_proxy NO_PROXY

rm -f /etc/apt/apt.conf /etc/apt/apt.conf.d/*proxy* || true
printf 'Acquire::http::Proxy "false";\nAcquire::https::Proxy "false";\n' \
    > /etc/apt/apt.conf.d/00no-proxy

git config --system --unset-all http.proxy || true
git config --system --unset-all https.proxy || true

if [ -f /var/jenkins_home/.gitconfig ]; then
    git config --global --unset-all http.proxy || true
    git config --global --unset-all https.proxy || true
fi

exec /usr/bin/tini -- /usr/local/bin/jenkins.sh "$@"