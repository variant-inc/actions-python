import asyncio
from pathlib import Path

import botocore
from loguru import logger

from multideploy.config import settings
from multideploy.exceptions import TrivyException
from multideploy.utils import assume_role, base_dir, boto_client, multiline_log_printer


async def pull_trivy_ignore():
    creds = await assume_role(
        "arn:aws:iam::108141096600:role/ops-github-runner", "ops-s3"
    )

    async with boto_client.resource("s3", **creds) as s3:
        logger.info("Downloading root trivy file from s3")

        trivy_bucket = await s3.Bucket(settings.TRIVY_S3_BUCKET_NAME)

        await trivy_bucket.download_file(
            ".trivyignore", base_dir / ".trivyignore"
        )  # TODO can be pulled once

        try:
            with open(base_dir / ".trivyignore", "ab") as f:
                await trivy_bucket.download_fileobj(base_dir.name + "/.trivyignore", f)
        except botocore.exceptions.ClientError as e:
            if e.response["Error"]["Code"] == "404":
                logger.info(f"trivyignore for repo {base_dir.name} does not exist.")
            else:
                raise

    with open(base_dir / ".trivyignore") as f:
        logger.info(f"Printing trivy ignore file for repo {base_dir.name}")
        logger.info(f.read())


async def run_trivy_scan(image_name: str, repo_dir: Path):
    repo_name = repo_dir.name
    logger.info(f"Running trivy scan for {repo_name}")
    await pull_trivy_ignore()

    trivy_low = asyncio.create_subprocess_shell(
        f"trivy image --ignore-unfixed --severity=HIGH,MEDIUM,LOW,UNKNOWN {image_name}",
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
        cwd=base_dir,
    )
    trivy_critical = asyncio.create_subprocess_shell(
        f"trivy image --ignore-unfixed --exit-code 1 --severity=CRITICAL {image_name}",
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
        cwd=base_dir,
    )
    proc = await trivy_low
    stdout, stderr = await proc.communicate()
    multiline_log_printer(repo_name, "trivy_low", "INFO", stdout)

    if proc.returncode > 0:
        multiline_log_printer(repo_name, "trivy_low", "ERROR", stderr)
        raise TrivyException

    proc = await trivy_critical
    stdout, stderr = await proc.communicate()

    multiline_log_printer(repo_name, "trivy_critical", "INFO", stdout)

    if proc.returncode > 0:
        multiline_log_printer(repo_name, "trivy_critical", "ERROR", stderr)
        raise TrivyException
