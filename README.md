# Actions Python

Action for CI workflow for python applications

<!-- action-docs-description -->
## Description

Github Action to perform build, test , scan and generate Image for Python

## Permissions

Add the following permissions to the job

```yaml
permissions:
  id-token: write
  contents: read
```

## Usage

```yaml
    - name: Actions Python
      uses: variant-inc/actions-python@v2
      with:
        ecr_repository: 'demo/example'
        python-version: 3.10
```

## Locating Container Images

ECR containers can be located with this URI.

```text
064859874041.dkr.ecr.us-east-2.amazonaws.com/<ecr_repository>
```
<!-- action-docs-description -->

<!-- action-docs-inputs -->
## Inputs

| parameter | description | required | default |
| --- | --- | --- | --- |
| dockerfile_dir_path | Directory Path to the dockerfile. | `false` | . |
| ecr_repository | ECR Repository Name. If this is empty, then container image will not be created.  | `false` |  |
| cloud_region | Region where the image will be created.  | `false` | us-east-2 |
| python-version | The python-version input is optional. If not supplied, the action will try to resolve the version from the default `.python-version` file.  If the `.python-version` file doesn't exist Python or PyPy version from the PATH will be used.  The default version of Python or PyPy in PATH varies between runners and can be changed unexpectedly so we recommend always setting Python version explicitly using the python-version inputs.  | `false` |  |
<!-- action-docs-inputs -->

<!-- action-docs-outputs -->

<!-- action-docs-outputs -->

<!-- action-docs-runs -->
## Runs

This action is a `composite` action.
<!-- action-docs-runs -->
