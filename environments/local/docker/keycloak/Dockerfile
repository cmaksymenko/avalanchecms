ARG KEYCLOAK_VERSION=23.0

# Stage 1: Build Stage with isolated install directory
FROM registry.access.redhat.com/ubi9 AS ubi-micro-build
RUN mkdir -p /mnt/rootfs

# Install jq with minimal dependencies and no docs, clean cache, and remove
# 'setup' to optimize for a lightweight container environment

RUN dnf install --installroot /mnt/rootfs jq-1.6-* --releasever 9 --setopt install_weak_deps=false --nodocs -y && \
    dnf --installroot /mnt/rootfs clean all && \
    rpm --root /mnt/rootfs -e --nodeps setup

# ---

# Stage 2: Final Keycloak Image
FROM quay.io/keycloak/keycloak:${KEYCLOAK_VERSION}

# Transfer jq and dependencies from build stage
COPY --from=ubi-micro-build /mnt/rootfs /