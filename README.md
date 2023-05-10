# Actions Python

Action for CI workflow for python applications

<!-- action-docs-description -->
## Description

Github action to perform build, test , scan and generate image.
<!-- action-docs-description -->

<!-- action-docs-inputs -->
## Inputs

| parameter | description | required | default |
| --- | --- | --- | --- |
| dockerfile_dir_path | Directory path to the dockerfile | `false` | . |
| ecr_repository | ECR repository name | `true` |  |
| container_push_enabled | Enable Build and Push Container Image | `true` | true |
| python-version | The python-version input is optional. If not supplied, the action will try to resolve the version from the default `.python-version` file. If the `.python-version` file doesn't exist Python or PyPy version from the PATH will be used. The default version of Python or PyPy in PATH varies between runners and can be changed unexpectedly so we recommend always setting Python version explicitly using the python-version or python-version-file inputs.  | `false` |  |
<!-- action-docs-inputs -->

<!-- action-docs-outputs -->

<!-- action-docs-outputs -->

<!-- action-docs-runs -->
## Runs

This action is a `composite` action.
<!-- action-docs-runs -->

## Prerequisites

### 1. Setup GitHub action workflow

1. On GitHub, navigate to the main page of the repository.
2. Under your repository name, click Actions.
3. Find the template that matches the language and tooling you want to use, then click Set up this workflow. Either start with blank workflow or choose any integration workflows.

### 2. Add actions-setup

1. Add a code checkout step this will be needed to add code to the GitHub workspace.

    ```yaml
     - uses: actions/checkout@v2
       with:
         fetch-depth: 0
    ```

2. This is to add some global environment variables that are used as part of the python action. It will output `image_version`.

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
         github_token: ${{ secrets.GITHUB_TOKEN }}
    ```

2. (Optionally) Add Script to run before running workflow.

    In `.github/actions`, add a file named `pre_test.sh` that will run any commands required for testing your codebase using this action. You will need to you a package manager supported by Debian Linux

    Example:

    ```bash
    apt-get install --no-cache \
      git \
      curl
    ```

## Using Python Action

You can set up continuous integration for your project using this workflow action.
After you set up CI, you can customize the workflow to meet your needs. By passing the right input parameters with the actions python.
