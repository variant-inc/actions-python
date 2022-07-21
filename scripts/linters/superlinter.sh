#!/usr/bin/env bash

# set -e

image="github/super-linter:slim-v4"
# shellcheck disable=SC2046
cleanup() {
  echo "Cleaning up..."
  docker stop $(docker ps -a | grep "$1" | awk -F ' ' '{print $1}') && \
  docker rm $(docker ps -a | grep "$1" | awk -F ' ' '{print $1}') &> /dev/null
}

# trap cleanup $image EXIT

docker pull $image

docker run -e RUN_LOCAL=true \
  -e VALIDATE_PYTHON_BLACK=false \
  -e VALIDATE_PYTHON_ISORT=false \
  -e VALIDATE_PYTHON_MYPY=false \
  -e VALIDATE_PYTHON_FLAKE8=false \
  -e VALIDATE_ALL_CODEBASE=true \
  -e VALIDATE_GITHUB_ACTIONS=false \
  -e VALIDATE_TERRAFORM_TFLINT=false \
  -e VALIDATE_KUBERNETES_KUBEVAL=false \
  -e "FILTER_REGEX_EXCLUDE=.*env/.*" \
  -e "LOG_LEVEL=VERBOSE" \
  -v "$(pwd)":/tmp/lint \
  $image

cleanup $image &> /dev/null