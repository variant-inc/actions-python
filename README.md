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

## Usage

```yaml
  - name: Actions Python
    id: actions-python
    uses: variant-inc/actions-python@v2
    with:
      ecr_repository: demo/example
      python-version: 3.10
```
