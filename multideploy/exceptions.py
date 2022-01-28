class DeployException(Exception):
    pass

class TrivyException(DeployException):
    step_name = "trivy scan"

class CoverageScanException(DeployException):
    step_name = "coverage scan"

class BuildException(DeployException):
    step_name = "docker image build"