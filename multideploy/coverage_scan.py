import asyncio
import shutil
from pathlib import Path

from loguru import logger

from multideploy.config import settings
from multideploy.exceptions import CoverageScanException
from multideploy.utils import detect_main_branch, docker_client, multiline_log_printer

COMMON_SONAR_CONFIG = {
    "host.url": "https://sonarcloud.io",
    "organization": settings.SONAR_ORG,
    "projectKey": settings.SONAR_PROJECT_KEY,
    "projectName": "",
    "python.coverage.reportPaths": "coverage.xml",
    "login": settings.SONAR_TOKEN,
    "sourceEncoding": "UTF-8",
    "python.version": "3.10",
    "python.xunit.reportPaths": "results.xml",
    "coverage.dtdVerification": "false",
}


async def run_coverage_scan(docker_image, lambda_path: Path):
    lambda_name = lambda_path.name
    logger.info(f"Running coverage scan for {lambda_name}")

    real_path = Path("/runner/_work/_temp/_github_workflow")  # real path on host
    container_path = Path("/test_artifacts")  # path mounted in a container
    local_path = Path("/github/workflow")

    volumes = {str(real_path): {"bind": str(container_path), "mode": "rw"}}
    container = docker_client.containers.run(
        docker_image,
        remove=True,
        detach=True,
        tty=True,
        entrypoint="bash",
        volumes=volumes,
    )
    await generate_coverage(container, lambda_name, container_path / lambda_name)

    # cleanup
    container.stop()

    local_path = local_path / lambda_name
    await sonar_scan(lambda_path, local_path)
    shutil.rmtree(local_path)


async def generate_coverage(container, lambda_name: str, container_path: Path):

    script_to_run = (
        "bash -c 'pip install coverage pytest mock moto pytest-freezegun &&"
        f"mkdir -p {container_path} && coverage run -m pytest &&"
        f"python -m coverage xml -i -o {container_path / 'coverage.xml'}'"
    )
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

    logger.info(f"List of artifacts: {list(local_path.glob('*'))}")
    sonar_args["projectKey"] = sonar_args["projectKey"] + "-" + lambda_name
    sonar_args["projectName"] = lambda_path.name
    sonar_args["python.coverage.reportPaths"] = local_path / "coverage.xml"
    sonar_args["scm.revision"] = settings.GITHUB_SHA

    branch_name = settings.BRANCH_NAME
    logger.info(f"Branch name: {settings.BRANCH_NAME}")

    if "pull" in branch_name:
        sonar_args["pullRequest.key"] = branch_name.split("/")[1]

    elif "/" not in branch_name:
        sonar_args["branch.name"] = branch_name
        if detect_main_branch():
            sonar_args["qualitygate.wait"] = "true"
    else:
        raise NotImplementedError(f"{branch_name} not supported")

    sonar_args = " ".join(
        [f"-Dsonar.{key}={value}" for key, value in sonar_args.items()]
    )
    # TODO add dir to sonarcloud monorepo automatically when not exists
    proc = await asyncio.create_subprocess_shell(
        f"sonar-scanner {sonar_args}",
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
        cwd=lambda_path,
    )
    stdout, stderr = await proc.communicate()
    multiline_log_printer(lambda_name, "sonar-scanner", "INFO", stdout)

    if proc.returncode > 0:
        multiline_log_printer(lambda_name, "sonar-scanner", "ERROR", stderr)
        raise CoverageScanException
