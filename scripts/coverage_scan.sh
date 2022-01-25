#!/bin/bash
set -euo pipefail

echo "---Start: tests"
REQUIREMENTS_TXT="requirements.txt"
echo "---pip install"
if [ -f "$REQUIREMENTS_TXT" ]; then
  if [ "$INPUT_TEST_FRAMEWORK" != unittest ]; then
    python -m venv env
    # shellcheck source=/dev/null
    source env/bin/activate
  fi
  pip install --requirement "$REQUIREMENTS_TXT"
else
  python -m pip install --upgrade pipenv
  pipenv sync --dev --system
fi

pip install --upgrade wheel coverage

# shellcheck disable=SC1091
if [ "$INPUT_TEST_FRAMEWORK" = pytest ]; then
  pip install --upgrade pytest &&
    coverage run -m pytest
elif [ "$INPUT_TEST_FRAMEWORK" = unittest ]; then
  coverage run -m unittest discover
else
  echo "Unsupported Test Framework"
  exit 1
fi

coverage xml -i -o coverage.xml
echo "----End: tests"

pull_number=$(jq --raw-output .pull_request.number "$GITHUB_EVENT_PATH")
export PULL_REQUEST_KEY=$pull_number

echo "------Sonar tests."

sonar_args="-Dsonar.host.url=https://sonarcloud.io \
            -Dsonar.login=$SONAR_TOKEN \
            -Dsonar.scm.revision=$GITHUB_SHA \
            -Dsonar.python.coverage.reportPaths=coverage.xml"

if [ "$PULL_REQUEST_KEY" = null ]; then
  echo "Sonar run when pull request key is null."
  eval "sonar-scanner $sonar_args -Dsonar.branch.name=$BRANCH_NAME"

else
  echo "Sonar run when pull request key is not null."
  eval "sonar-scanner $sonar_args -Dsonar.pullrequest.key=$PULL_REQUEST_KEY"
fi
