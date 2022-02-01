import asyncio
import json
import os
from pathlib import Path
import aioboto3
import asyncio
import botocore
import docker

from checksumdir import dirhash
from loguru import logger
from multideploy.config import settings
from multideploy.utils import boto_client


async def load_image_hash(repository_name: str, image_tag: str):
    async with boto_client.client("ecr") as ecr:
        try:
            output = await ecr.batch_get_image(
                registryId=settings.ECR_REGISTRY_ID,
                repositoryName=repository_name,
                imageIds=[{"imageTag": image_tag}],
                acceptedMediaTypes=[
                    "application/vnd.docker.distribution.manifest.v1+json"
                ],
            )
        except botocore.exceptions.ClientError as error:
            if error.response["Error"]["Code"] == "RepositoryNotFoundException":
                logger.info(f"Repository {repository_name} not found, will be created.")
                return ""
            else:
                raise error

        if not output["images"]:
            logger.info(
                f"No images found for repository {repository_name} (looking for images"
                f" with tag {image_tag})"
            )
            return ""
        manifest = output["images"][0]["imageManifest"]
        v1_manifest = json.loads(manifest)["history"][0]["v1Compatibility"]
        labels = json.loads(v1_manifest)["config"]["Labels"]
        # proposed hash label: com.drivevariant.dataops.lambda_dir_hash
        return labels


async def calc_dir_hash(repo_dir: Path):
    return dirhash(
        repo_dir,
        "md5",
        ignore_hidden=True,
        excluded_files=[".*", ".*/", "*.pyc"],
    )

    # while building remember to not tag "latest" but with merge number
    # compare merge request builds with latests
    # versioning with git short hash

    # scan repo for dirs
    # load default dockerfile from .common if dockerfile not found in dir