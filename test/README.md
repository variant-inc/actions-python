# Actions Test Python

Action for CI workflow for python applications

<!-- action-docs-description -->
## Description

Github Action to Build & Test Python

RequiredEnv:
  GITHUB_TOKEN
  SONAR_TOKEN
<!-- action-docs-description -->

<!-- action-docs-inputs -->
## Inputs

| parameter | description | required | default |
| --- | --- | --- | --- |
| python-version | The python-version input is optional. If not supplied, the action will try to resolve the version from the default `.python-version` file.  If the `.python-version` file doesn't exist Python or PyPy version from the PATH will be used.  The default version of Python or PyPy in PATH varies between runners and can be changed unexpectedly so we recommend always setting Python version explicitly using the python-version inputs. | `false` | |
| sonar_wait_flag | Says if Sonar has to wait for analysis | `false` | |
<!-- action-docs-inputs -->

<!-- action-docs-outputs -->

<!-- action-docs-outputs -->

<!-- action-docs-runs -->
## Runs

This action is a `composite` action.
<!-- action-docs-runs -->
