import asyncio
from pathlib import Path

from loguru import logger
import botocore

from multideploy.config import settings
from multideploy.exceptions import TrivyException
from multideploy.utils import base_dir, boto_client, multiline_log_printer, assume_role


async def pull_trivy_ignore():
    creds = await assume_role(
        "arn:aws:iam::108141096600:role/ops-github-runner", "ops-s3"
    )

    async with boto_client.resource("s3", **creds) as s3:
        logger.info("Download root trivy file from s3")

        trivy_bucket = await s3.Bucket(settings.TRIVY_S3_BUCKET_NAME)

        await trivy_bucket.download_file(".trivyignore", base_dir / ".trivyignore")

        trivy_dir = base_dir / "trivy"
        trivy_dir.mkdir(exist_ok=True)

        try:
            await trivy_bucket.download_file(
                base_dir.name + "/.trivyignore", trivy_dir / ".trivyignore"
            )
        except botocore.exceptions.ClientError as e:
            if e.response["Error"]["Code"] == "404":
                logger.info(f"trivyignore for repo {base_dir.name} does not exist.")
            else:
                raise
    breakpoint()


async def run_trivy_scan(image_name: str, repo_dir: Path):
    repo_name = repo_dir.name

    await pull_trivy_ignore()

    trivy_low = asyncio.create_subprocess_shell(
        f"trivy image --severity=HIGH,MEDIUM,LOW,UNKNOWN {image_name}",
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    trivy_critical = asyncio.create_subprocess_shell(
        f"trivy image --exit-code 1 --severity=CRITICAL {image_name}",
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
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