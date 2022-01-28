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

base_dir = Path("/data-lambda-functions")
repo = Repo(base_dir)
short_hash = repo.git.rev_parse(repo.head.object.hexsha, short=7)
