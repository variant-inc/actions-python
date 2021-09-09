#!/bin/bash

function finish {
  set -x
  sudo chown -R 1000:1000 "$GITHUB_WORKSPACE"/*
  sudo git clean -fdx
  set +x
}

trap finish EXIT
setfacl -d -Rm u:1000:rwx "$GITHUB_WORKSPACE"

set -xeo

echo "---Start: Setting Prerequisites"
cd "$GITHUB_WORKSPACE"
echo "Current directory: $(pwd)"

echo "Cloning into actions-collection..."
git clone -b v1 https://github.com/variant-inc/actions-collection.git ./actions-collection

export AWS_WEB_IDENTITY_TOKEN_FILE="/token"
echo "$AWS_WEB_IDENTITY_TOKEN" >> "$AWS_WEB_IDENTITY_TOKEN_FILE"

export AWS_DEFAULT_REGION="${AWS_DEFAULT_REGION:=us-east-1}"

export BRANCH_NAME="$GITVERSION_BRANCHNAME"
echo "Print Branch name: $BRANCH_NAME"

export GITHUB_USER="$GITHUB_REPOSITORY_OWNER"
echo "---End: Setting Prerequisites"

echo "---Start: pip install"
chown -R 1000:1000 "$GITHUB_WORKSPACE"/*
REQUIREMENTS_TXT="./requirements.txt"

if [ -f "$REQUIREMENTS_TXT" ]; then
  python -m pip install -r $REQUIREMENTS_TXT
else
  python -m pip install --upgrade pipenv wheel
  pipenv install --dev
fi

echo "---End: pip install"

echo "---Start: pytest test"
coverage run -m pytest test
echo "---End: pytest test"

echo "---Start: Sonar Scan"
sh -c "/scripts/coverage_scan.sh"
echo "---End: Sonar Scan"


echo "Container Push: $INPUT_CONTAINER_PUSH_ENABLED"
if [ "$INPUT_CONTAINER_PUSH_ENABLED" = 'true' ]; then
  echo "Start: Checking ECR Repo"
  ./actions-collection/scripts/ecr_create.sh "$INPUT_ECR_REPOSITORY"
  echo "End: Checking ECR Repo"
  echo "Start: Publish Image to ECR"
  ./actions-collection/scripts/publish.sh
  echo "End: Publish Image to ECR"
fi

echo "---Start: Clean up"
sudo git clean -fdx
echo "---End: Clean up"