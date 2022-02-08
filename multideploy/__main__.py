import asyncio
import os

from loguru import logger

from multideploy.build_image import build_image
from multideploy.calc_checksum import calc_dir_hash, load_image_hash
from multideploy.config import ecr_repo_name, settings
from multideploy.coverage_scan import run_coverage_scan
from multideploy.ecr_push import ecr_push
from multideploy.exceptions import DeployException
from multideploy.trivy_scan import run_trivy_scan
from multideploy.utils import base_dir, docker_login


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
        current_hash = await d["current_hash"]
        image_hash = await d["image_hash"]

        if current_hash != image_hash:
            logger.info(
                f"Diffrent checksum for {repo_name}, "
                f"(current_hash) {current_hash} != {image_hash}"
            )
            repos_to_update[repo_name] = (
                d["repo_dir"],
                current_hash,
            )
        else:
            logger.info(
                f"No different checksum for {repo_name},"
                f"skipping. (current_hash) {current_hash} == {image_hash}"
            )

    await docker_login_proc
    # update repos
    for repo_name, (repo_dir, current_hash) in repos_to_update.items():
        image = await build_image(repo_dir, current_hash)
        await run_trivy_scan(image.tags[0], repo_dir)
        await run_coverage_scan(image.tags[0], repo_dir)
        await ecr_push(image, repo_name)


if __name__ == "__main__":
    if os.name == "nt":  # windows fix
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

    try:
        asyncio.run(main())
    except DeployException as e:
        logger.error(f"Deploy failed at step: {e.step_name}")
        exit(1)
