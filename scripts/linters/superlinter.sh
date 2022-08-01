#!/usr/bin/env bash

set -e

image=github/super-linter:slim-v4

docker pull $image

docker run --rm \
  -e RUN_LOCAL=true \
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