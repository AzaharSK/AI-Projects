# Use the Jenkins image as the base image
FROM jenkins/jenkins:lts

# Switch to root user to install dependencies
USER root

# Strip ALL proxy configuration that Jenkins base image may bake in,
# then install Docker and Python3. The ENV directives clear proxy vars
# for every subsequent RUN layer AND for runtime containers.
ENV http_proxy="" \
    https_proxy="" \
    HTTP_PROXY="" \
    HTTPS_PROXY="" \
    all_proxy="" \
    ALL_PROXY="" \
    no_proxy="" \
    NO_PROXY=""

RUN set -eux; \
    rm -f /etc/apt/apt.conf.d/*proxy* /etc/apt/apt.conf; \
    printf 'Acquire::http::Proxy "false";\nAcquire::https::Proxy "false";\n' \
        > /etc/apt/apt.conf.d/00no-proxy; \
    apt-get update -y; \
    apt-get install -y --no-install-recommends \
        docker.io ca-certificates curl python3 python3-pip; \
    rm -rf /var/lib/apt/lists/*

# Add Jenkins user to the Docker group (create if it doesn't exist)
RUN groupadd -f docker && \
    usermod -aG docker jenkins

COPY --chown=root:root docker-entrypoint.sh /usr/local/bin/docker-entrypoint.sh
RUN chmod 755 /usr/local/bin/docker-entrypoint.sh

# Create the Docker directory and volume for DinD
RUN mkdir -p /var/lib/docker
VOLUME /var/lib/docker

ENTRYPOINT ["/usr/local/bin/docker-entrypoint.sh"]

# Switch back to the Jenkins user
USER jenkins