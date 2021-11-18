# Actions Python
Action for CI workflow for python applications

- [Actions Python](#actions-python)
  - [Prerequisites](#prerequisites)
    - [1. Setup github action workflow](#1-setup-github-action-workflow)
    - [2. Add actions-setup](#2-add-actions-setup)
    - [3. Add actions-python](#3-add-actions-python)
    - [4. Add octopus action](#4-add-octopus-action)
  - [Using Python Action](#using-python-action)
    - [Adding actions-python to workflow](#adding-actions-python-to-workflow)
    - [Input Parameters](#input-parameters)
    - [Pre Test Script (optional)](#pre-test-script-optional)
      - [Example (actions-python)](#example-actions-python)

  - [Using Python Action](#using-python-action)
    - [Adding actions-python to workflow](#adding-actions-python-to-workflow)
  - [parameters](#parameters)
    - [Input Parameters](#input-parameters)

## Prerequisites

### 1. Setup github action workflow

1. On GitHub, navigate to the main page of the repository.
2. Under your repository name, click Actions.
3. Find the template that matches the language and tooling you want to use, then click Set up this workflow. Either start with blank workflow or choose any integration workflows.

### 2. Add actions-setup

1. Add a code checkout step this will be needed to add code to the github workspace.

```yaml
    - uses: actions/checkout@v2
      with:
        fetch-depth: 0
```

1. This is to add some global environment variables that are used as part of the python action. It will output `image_version`.

```yaml
    - name: Setup
      uses: variant-inc/actions-setup@v1
        id: actions-setup
        
```

Refer [actions-setup](https://github.com/variant-inc/actions-setup) for documentation.

### 3. Add actions-python

1. This step is to invoke the python action with release version by passing environment variables and input parameters. Input parameters section provides more insight of optional and required parameters.

```yaml

    - name: Actions Python
      id: actions-python
      uses: variant-inc/actions-python@v1
      env:
        AWS_DEFAULT_REGION: us-east-1
      with:
        dockerfile_dir_path: '.'
        ecr_repository: naveen-demo-app/demo-repo
```

2. (Optionally) Add Script to run before running workflow.

    In `.github/actions`, add a file named `pre_test.sh` that will run any commands required for testing your codebase using this action. You will need to you a package manager supported by Debian Linux

    Example:
    ```bash
    apt-get install --no-cache \
      git \
      curl
    ```

### 4. Add octopus action

1. Adding octopus action will add ability to set up continuous delivery to octopus. This action can be invoked by action name and release version.

```yaml

    - name: Actions Octopus
      uses: variant-inc/actions-octopus@v1
      with:
        default_branch: ${{ env.MASTER_BRANCH }}
        deploy_scripts_path: deploy
        project_name: ${{ env.PROJECT_NAME }}
        version: ${{ steps.actions-setup.outputs.image-version }}
        space_name: ${{ env.OCTOPUS_SPACE_NAME }}

```

Refer [octopus action](https://github.com/variant-inc/actions-octopus) for documentation.

## Using Python Action

You can set up continuous integration for your project using this workflow action.
After you set up CI, you can customize the workflow to meet your needs. By passing the right input parameters with the actions python.

### Adding actions-python to workflow

Sample snippet to add actions-python to your workflow code.
See [action.yml](action.yml) for the full documentation for this action's inputs and outputs.

```yaml
jobs:
  build_test_scan:
    runs-on: eks
    name: CI Pipeline
    steps:
    - uses: actions/checkout@v2
      with:
        fetch-depth: 0

    - name: Actions Setup
      uses: variant-inc/actions-setup@v1
        id: actions-setup

    - name: Actions Python
      id: actions-python
      uses: variant-inc/actions-python@v1
      env:
        AWS_DEFAULT_REGION: us-east-1
        AWS_REGION: us-east-1
      with:
        dockerfile_dir_path: '.'
        ecr_repository: naveen-demo-app/demo-repo

    - name: Actions Octopus
      uses: variant-inc/actions-octopus@v1
      with:
        default_branch: ${{ env.MASTER_BRANCH }}
        deploy_scripts_path: deploy
        project_name: ${{ env.PROJECT_NAME }}
        version: ${{ steps.actions-setup.outputs.image-version }}
        space_name: ${{ env.OCTOPUS_SPACE_NAME }}

```

### Input Parameters

| Parameter                     | Default         | Description                                                                                                                  | Required |
| ----------------------------- | --------------- | ---------------------------------------------------------------------------------------------------------------------------- | -------- |
| `dockerfile_dir_path`         | `.`             | Directory path to the dockerfile                                                                                             | true     |
| `ecr_repository`              |                 | ECR Repository name                                                                                                          | true     |
| `container_push_enabled`      | "true"          | Enable build and push container image                                                                                        | true     |


### Pre Test Script (optional)

When using actions-python create a file in .github/actions/pre_test.sh.

Include any dependant packages your app requires when testing. These packages will need to be installed using a Debian package manager.

#### Example (actions-python)
```bash
#!/bin/bash

echo "____INSTALLING_SVN_____"
apt-get install --no-install-recommends -y \
subversion

echo "____INSTALLING_PWSH_____"
wget https://packages.microsoft.com/config/debian/10/packages-microsoft-prod.deb
dpkg -i packages-microsoft-prod.deb
apt-get install -y powershell
```
