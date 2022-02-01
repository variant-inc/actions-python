from pathlib import Path

import docker
from git import Repo
from loguru import logger
import aioboto3


def multiline_log_printer(
    lambda_name: str,
    func_name: str,
    log_level: str,
    log,
):
    log_patch_func = lambda r: r.update(function=lambda_name, name=func_name, line="")

    for line in log.decode().split("\n")[:-1]:
        logger.patch(log_patch_func).log(log_level, line)


docker_client = docker.from_env()
boto_client = aioboto3.Session(region_name="us-east-1")

base_dir = Path("/github/workspace")
repo = Repo(base_dir)
short_hash = repo.git.rev_parse(repo.head.object.hexsha, short=7)


async def assume_role(role_arn: str, session_name: str) -> dict:
    async with boto_client.client("sts") as sts:
        assumed_role_object = await sts.assume_role(
            RoleArn=role_arn, RoleSessionName=session_name
        )
        credentials = assumed_role_object["Credentials"]

        return {
            "aws_access_key_id": credentials["AccessKeyId"],
            "aws_secret_access_key": credentials["SecretAccessKey"],
            "aws_session_token": credentials["SessionToken"],
        }
