import asyncio
import os
from pathlib import Path

from loguru import logger

from multideploy.build_image import build_image
from multideploy.calc_checksum import calc_dir_hash, load_image_hash
from multideploy.config import ecr_repo_name, settings
from multideploy.coverage_scan import run_coverage_scan
from multideploy.ecr_push import ecr_push
from multideploy.exceptions import DeployException
from multideploy.trivy_scan import run_trivy_scan
from multideploy.utils import base_dir, docker_login

logger.add(
    "/output.log",
    format="{message}\n\n",
    enqueue=True,
    filter=lambda record: "summary" in record["extra"],
)


async def main():
    docker_login_proc = docker_login()
    dir_hash = {}

    latest_tag = "latest"
    """
        pick up all directories in base_dir
        calculate their checksum + load image checksum
    """
    paths_to_check = []

    for dir_to_check in settings.INPUT_MULTIREPO_SCAN_PATH:
        paths_to_check.extend((base_dir / dir_to_check).iterdir())

    for repo_dir in paths_to_check:
        if not repo_dir.is_dir() or repo_dir.name in settings.REPO_IGNORE_DIRS:
            continue

        if not (repo_dir / "Dockerfile").exists():
            logger.info(
                f"No Dockerfile found in {repo_dir}, "
                "assuming the folder contains infrastructure code only. Skipping."
            )
            continue

        dir_hash[repo_dir.name] = {
            "current_hash": asyncio.create_task(calc_dir_hash(repo_dir)),
            "image_hash": asyncio.create_task(
                load_image_hash(f"{ecr_repo_name}/{repo_dir.name}", latest_tag)
            ),
            "repo_dir": repo_dir,
        }

    # check what repos need to be updated (diffrent checksum)
    repos_to_update = {}
    for repo_name, d in dir_hash.items():
        current_hash = await d["current_hash"]
        image_hash = await d["image_hash"]

        if current_hash != image_hash:
            logger.info(
                f"Diffrent checksum for {repo_name}, "
                f"(current_hash) {current_hash} != {image_hash}"
            )
            logger.info(f"{repo_name} different checksum, updating", summary=True)
            repos_to_update[repo_name] = (
                d["repo_dir"],
                current_hash,
            )
        else:
            logger.info(
                f"Same checksum for {repo_name},"
                f" skipping. (current_hash) {current_hash} == {image_hash}"
            )
            logger.info(f"{repo_name} same checksum, skipping", summary=True)

    await docker_login_proc

    repos_to_process = []
    # update repos
    for repo_name, (repo_dir, current_hash) in repos_to_update.items():
        repos_to_process.append(
            asyncio.create_task(process_repo(repo_dir, repo_name, current_hash))
        )

    await asyncio.gather(*repos_to_process)


async def process_repo(repo_dir: Path, repo_name: str, current_hash: str):
    image = await build_image(repo_dir, current_hash)
    await run_trivy_scan(image.tags[-1], repo_dir)
    await run_coverage_scan(image.tags[-1], repo_dir)
    await ecr_push(image, repo_name)


if __name__ == "__main__":
    if os.name == "nt":  # windows fix
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

    try:
        asyncio.run(main())
    except DeployException as e:
        logger.error(f"Deploy failed at step: {e.step_name}")
        exit(1)
