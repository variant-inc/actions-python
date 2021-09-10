FROM python:slim-buster

ARG BUILD_DATE
ARG BUILD_REVISION
ARG BUILD_VERSION

LABEL com.github.actions.name="Lazy Action Python" \
  com.github.actions.description="Build and Push Python Image" \
  com.github.actions.icon="code" \
  com.github.actions.color="red" \
  maintainer="Variant DevOps <devops@drivevariant.com>" \
  org.opencontainers.image.created=$BUILD_DATE \
  org.opencontainers.image.revision=$BUILD_REVISION \
  org.opencontainers.image.version=$BUILD_VERSION \
  org.opencontainers.image.authors="Variant DevOps <devops@drivevariant.com>" \
  org.opencontainers.image.url="https://github.com/variant-inc/actions-python" \
  org.opencontainers.image.source="https://github.com/variant-inc/actions-python" \
  org.opencontainers.image.documentation="https://github.com/variant-inc/actions-python" \
  org.opencontainers.image.vendor="AWS ECR" \
  org.opencontainers.image.description="Build and Push Python Packages"



ARG GLIBC_VER=2.31-r0
ENV AWS_PAGER=""
# dockerfile_lint - ignore
RUN apt-get update &&\
  apt-get install \
  --no-install-recommends \
  --assume-yes \
  git \
  wget \
  bash \
  sudo \
  curl \
  tzdata \
  ca-certificates \
  openjdk-11-jdk \
  jq \
  unzip \
  gzip \
  binutils \
  iptables \
  libdevmapper1.02.1 &&\
  rm -rf matching cache rm /var/lib/apt/lists/* &&\
  python -m pip --no-cache-dir install coverage

# dockerfile_lint - ignore
RUN rm -rf /var/lib/apt/lists/* &&\
  \
  curl -sL https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip -o awscliv2.zip &&\
  unzip awscliv2.zip &&\
  aws/install &&\
  rm -rf \
  awscliv2.zip \
  aws \
  /usr/local/aws-cli/v2/*/dist/aws_completer \
  /usr/local/aws-cli/v2/*/dist/awscli/data/ac.index \
  /usr/local/aws-cli/v2/*/dist/awscli/examples \
  glibc-${GLIBC_VER}.apk \
  glibc-bin-${GLIBC_VER}.apk &&\
  rm -rf /var/cache/apt/* &&\
  aws --version &&\
  set -x &&\
    curl -sL https://download.docker.com/linux/debian/dists/buster/pool/stable/amd64/containerd.io_1.4.9-1_amd64.deb -o containerd.deb &&\
    dpkg -i  containerd.deb &&\
    curl -sL https://download.docker.com/linux/debian/dists/buster/pool/stable/amd64/docker-ce-cli_20.10.8~3-0~debian-buster_amd64.deb -o docker-ce-cli.deb &&\
    dpkg -i  docker-ce-cli.deb &&\
    curl -sL https://download.docker.com/linux/debian/dists/buster/pool/stable/amd64/docker-ce_20.10.8~3-0~debian-buster_amd64.deb -o docker-ce.deb &&\
    dpkg -i  docker-ce.deb





ARG SONAR_SCANNER_VERSION=4.4.0.2170
ENV PATH $PATH:/sonar-scanner/bin
RUN set -x \
  && curl --insecure -o /sonar-scanner-cli-${SONAR_SCANNER_VERSION}.zip \
    -L https://binaries.sonarsource.com/Distribution/sonar-scanner-cli/sonar-scanner-cli-${SONAR_SCANNER_VERSION}.zip \
  && unzip sonar-scanner-cli-${SONAR_SCANNER_VERSION}.zip \
  && mv -v /sonar-scanner-${SONAR_SCANNER_VERSION}  /sonar-scanner/  \
  && ln -s /sonar-scanner/bin/sonar-scanner       /usr/local/bin/     \
  && ln -s /sonar-scanner/bin/sonar-scanner-debug /usr/local/bin/ \
  && rm -f sonar-scanner-cli-*.zip


SHELL ["/bin/bash", "-e", "-o", "pipefail", "-c"]
RUN curl -sfL https://raw.githubusercontent.com/aquasecurity/trivy/master/contrib/install.sh | sh -s -- -b /usr/local/bin

COPY . /

RUN chmod +x -R /scripts/* /*.sh
ENTRYPOINT ["/entrypoint.sh"]
