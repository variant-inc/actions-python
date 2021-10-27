#!/bin/bash

set -euo pipefail

echo "---Start: pytest test"
REQUIREMENTS_TXT="requirements.txt"
echo "---pip install"
if [ -f "$REQUIREMENTS_TXT" ]; then
  # shellcheck disable=SC1091
  python -m venv env &&\
	  source env/bin/activate &&\
    python -m pip install --requirement "$REQUIREMENTS_TXT"
else
  python -m pip install --upgrade pipenv wheel
  pipenv install --dev
fi

python -m pip install pytest wheel coverage &&\
	coverage run -m pytest test &&\
	coverage xml -i -o coverage.xml
echo "---End: pytest test"

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
