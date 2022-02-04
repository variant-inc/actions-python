from pathlib import Path
import asyncio
import os

from loguru import logger

from multideploy.exceptions import DeployException
from multideploy.utils import base_dir, docker_login
from multideploy.config import settings, ecr_repo_name
from multideploy.calc_checksum import calc_dir_hash, load_image_hash
from multideploy.build_image import build_image 
from multideploy.coverage_scan import run_coverage_scan
from multideploy.trivy_scan import run_trivy_scan
from multideploy.ecr_push import ecr_push

async def main():
    docker_login_proc = docker_login()
    dir_hash = {}

    latest_tag = "latest"
    # pick up all directories in base_dir and calculate their checksum + load image checksum
    for repo_dir in base_dir.iterdir():
        if not repo_dir.is_dir() or repo_dir.name in settings.REPO_IGNORE_DIRS:
            continue

        dir_hash[repo_dir.name] = {
            "current_hash": calc_dir_hash(repo_dir),
            "image_hash": load_image_hash(
                f"{ecr_repo_name}/{repo_dir.name}", latest_tag
            ),
            "repo_dir": repo_dir,
        }

    # check what repos need to be updated (diffrent checksum)
    repos_to_update = {}
    for repo_name, d in dir_hash.items():
        current_hash = await d["current_hash"][settings.HASH_DOCKER_LABEL_NAME]
        image_hash = await d["image_hash"]

        if current_hash != image_hash:
            logger.info(
                f"Diffrent checksum for {repo_name}, (current_hash) {current_hash} !="
                f" {image_hash}"
            )
            repos_to_update[repo_name] = (
                d["repo_dir"], current_hash,
            )

    await docker_login_proc
    # update repos
    for repo_name, (repo_dir, current_hash) in repos_to_update.items():
        image = await build_image(repo_dir, current_hash)
        logger.info(f"Created image with tags {image.tags} for {repo_name}")
        logger.info(f"Running trivy scan for {repo_name}")
        await run_trivy_scan(image.tags[0], repo_dir)

        logger.info(f"Running coverage scan for {repo_name}")
        await run_coverage_scan(image.tags[0], repo_dir)

        logger.info(f"Pushing image {image.tags[0]} to ecr for {repo_name}")
        await ecr_push(image, repo_name)

if __name__ == "__main__":
    if os.name == "nt":  # windows fix
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

    try:
        asyncio.run(main())
    except DeployException as e:
        logger.error(f"Deploy failed at step: {e.step_name}")
        exit(1)
