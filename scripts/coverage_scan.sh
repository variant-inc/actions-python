#!/bin/bash
set -euo pipefail

sonar_logout() {
  exit_code=$?
  echo "Exit code is $exit_code"
  if [ "$exit_code" -eq 0 ]; then
    echo -e "\e[1;32m ________________________________________________________________\e[0m"
    echo -e "\e[1;32m Quality Gate Passed.\e[0m"
    echo -e "\e[1;32m ________________________________________________________________\e[0m"
  elif [ "$exit_code" -gt 0 ]; then
    set -e
    echo -e "\e[1;31m ________________________________________________________________\e[0m"
    echo -e "\e[1;31m ________________________________________________________________\e[0m"
    echo ""
    echo ""
    echo -e "\e[1;31m Sonar Quality Gate failed in $SONAR_PROJECT_KEY.\e[0m"
    echo ""
    echo ""
    echo -e "\e[1;31m ________________________________________________________________\e[0m"
    echo -e "\e[1;31m ________________________________________________________________\e[0m"
    exit 1 
  fi
}

trap "sonar_logout" EXIT

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

wait_flag="false"
if [ "$BRANCH_NAME" == "master" ] || [ "$BRANCH_NAME" == "main" ]; then
  wait_flag="true"
fi

SONAR_PROJECT_NAME="${INPUT_SONAR_PROJECT_NAME:=$SONAR_PROJECT_KEY}"

sonar_args="-Dsonar.host.url=https://sonarcloud.io \
            -Dsonar.login=$SONAR_TOKEN \
            -Dsonar.scm.revision=$GITHUB_SHA \
            -Dsonar.python.coverage.reportPaths=coverage.xml \
            -Dsonar.qualitygate.wait=$wait_flag \
            -Dsonar.projectKey=$SONAR_PROJECT_KEY"

if [ "$PULL_REQUEST_KEY" = null ]; then
  echo "Sonar run when pull request key is null."
  eval "sonar-scanner $sonar_args -Dsonar.branch.name=$BRANCH_NAME"

else
  echo "Sonar run when pull request key is not null."
  eval "sonar-scanner $sonar_args -Dsonar.pullrequest.key=$PULL_REQUEST_KEY"
fi
