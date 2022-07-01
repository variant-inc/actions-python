import base64
import os
from pathlib import Path

import aioboto3
import docker
from loguru import logger

from multideploy.config import settings


def multiline_log_printer(
    lambda_name: str,
    func_name: str,
    log_level: str,
    log,
):
    def log_patch_func(r):
        return r.update(function=lambda_name, name=func_name, line="")

    for line in log.decode().split("\n")[:-1]:
        logger.patch(log_patch_func).log(log_level, line)


docker_client = docker.from_env()
boto_client = aioboto3.Session(region_name="us-east-1")

base_dir = Path("/github/workspace")


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


DOCKER_LOGIN_SUCCEEDED = "Login Succeeded"


async def docker_login():
    async with boto_client.client("ecr") as ecr:
        response = await ecr.get_authorization_token()
        (
            docker_username,
            docker_password,
            docker_registry,
        ) = get_docker_username_password_registry(response)
        docker_login_response = docker_client.login(
            username=docker_username,
            password=docker_password,
            registry=docker_registry,
        )

        if DOCKER_LOGIN_SUCCEEDED == docker_login_response.get("Status"):
            logger.info(f"Logged into docker registry {docker_registry}")
        else:
            raise Exception(f"Failed to login to docker registry {docker_registry}")


def get_docker_username_password_registry(token):
    docker_username, docker_password = (
        base64.b64decode(token["authorizationData"][0]["authorizationToken"])
        .decode()
        .split(":")
    )
    docker_registry = token["authorizationData"][0]["proxyEndpoint"]
    return (docker_username, docker_password, docker_registry)


def detect_main_branch():
    return settings.BRANCH_NAME in ["master", "main"]


def append_to_step_summary(text: str):
    summary = os.getenv("GITHUB_STEP_SUMMARY")
    os.putenv("GITHUB_STEP_SUMMARY", summary + text)
