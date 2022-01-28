from pathlib import Path
import asyncio
import venv

from multideploy.utils import multiline_log_printer, docker_client

from multideploy.exceptions import CoverageScanException

COMMON_SONAR_CONFIG = {
    "host.url": "https://sonarcloud.io",
    "organization": "variant",
    "projectKey": "",
    "projectName": "",
    "python.coverage.reportPaths": "coverage.xml",
    "login": "",
    "scm.revision": "GITHUB_SHA",
    "sourceEncoding": "UTF-8",
    "python.version": "3.9",
    "python.xunit.reportPaths": "results.xml",
    "coverage.dtdVerification": "false",
}


async def run_coverage_scan(lambda_path: Path, docker_image):
    lambda_name = lambda_path.name

    local_path = Path("/tmp/") / lambda_name
    volumes = {local_path: {"bind": "/test_artifacts", "mode": "rw"}}
    container = docker_client.containers.run(
        docker_image,
        remove=True,
        detach=True,
        tty=True,
        entrypoint="bash",
        volumes=volumes,
    )

    await generate_coverage(container, lambda_name, local_path)

    # cleanup
    container.stop()
    await sonar_scan(lambda_path, local_path)


async def generate_coverage(container, lambda_name: str, local_path: Path):
    script_to_run = (
        "bash -c 'pip install coverage pytest mock moto &&" # TODO find a way to install it speed up
        "cd .. && coverage run -m pytest &&"
        f"python -m coverage xml -i -o {local_path / 'coverage.xml'}'"
    )
    # TODO install dev packages from pipenv if available
    exit_code, output = container.exec_run(script_to_run)

    if exit_code == 0:
        multiline_log_printer(lambda_name, "coverage scan", "INFO", output)
    else:
        multiline_log_printer(lambda_name, "coverage scan", "ERROR", output)
        container.stop()
        raise CoverageScanException


async def sonar_scan(lambda_path: Path, local_path: Path):
    lambda_name = lambda_path.name
    sonar_args = COMMON_SONAR_CONFIG.copy()

    sonar_args["projectKey"] = f"variant-inc_data-{lambda_path.name}"
    sonar_args["projectName"] = lambda_path.name
    sonar_args["python.coverage.reportPaths"] = local_path / "coverage.xml"

    sonar_args = " ".join(
        [f"-Dsonar.{key}={value}" for key, value in sonar_args.items()]
    )

    # TODO PR / master branch check
    """
    pull_number=$(jq --raw-output .pull_request.number "$GITHUB_EVENT_PATH")
    export PULL_REQUEST_KEY=$pull_number

     -Dsonar.branch.name=$BRANCH_NAME
     -Dsonar.pullrequest.key=$PULL_REQUEST_KEY
    """
    proc = await asyncio.create_subprocess_shell(
        f"sonar-scanner {sonar_args}",
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
        cwd=lambda_path,
    )
    stdout, stderr = await proc.communicate()
    multiline_log_printer(lambda_name, "sonar-scanner", "INFO", stdout)

    if proc.returncode != 1:
        multiline_log_printer(lambda_name, "sonar-scanner", "ERROR", stderr)
        raise CoverageScanException
