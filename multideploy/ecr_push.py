import urllib.parse

import requests
from docker.models.images import Image
from loguru import logger

from multideploy.config import ecr_repo_name, settings
from multideploy.utils import detect_main_branch, docker_client


async def ecr_create_if_not_present(ecr_repo: str):
    url_ecr_repo = urllib.parse.quote_plus(ecr_repo)
    headers = {"x-api-key": settings.LAZY_API_KEY}
    r = requests.get(
        f"https://{settings.LAZY_API_URL}/tenants/apps/"
        f"profiles/production/regions/{settings.AWS_REGION}/ecr/"
        f"repo/{url_ecr_repo}/repo-policy",
        headers=headers,
    )

    if r.status_code != 200:
        logger.info(f"Repo not found. Hence creating a new repo with name {ecr_repo}")
        r = requests.post(
            f"https://{settings.LAZY_API_URL}/tenants/apps/profiles/"
            f"production/regions/{settings.AWS_REGION}/ecr/repo",
            json={
                "profile": "production",
                "region": settings.AWS_REGION,
                "options": {
                    "repositoryName": ecr_repo,
                    "imageTagMutability": "MUTABLE",
                },
            },
            headers=headers,
        )
        r.raise_for_status()


async def ecr_push(image: Image, repo_name: str):
    logger.info(f"Pushing image {image.tags[0]} to ecr for {repo_name}")
    _, tag = image.tags[0].split(":", 1)
    ecr_name = f"{ecr_repo_name}/{repo_name}"
    await ecr_create_if_not_present(ecr_name)

    aws_repo_name = (
        f"{settings.ECR_REGISTRY_ID}.dkr.ecr.{settings.AWS_REGION}"
        f".amazonaws.com/{ecr_name}"
    )
    image.tag(aws_repo_name, tag=tag)

    tags = [tag]
    if detect_main_branch():
        latest_tag = "latest"
        image.tag(aws_repo_name, tag=latest_tag)
        tags.append(latest_tag)

    for line in docker_client.api.push(aws_repo_name, stream=True, decode=True):
        logger.info(line)

    logger.info(f"Pushed image named {aws_repo_name} with tags {tags}")
