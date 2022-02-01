from pathlib import Path

import docker
from loguru import logger

from multideploy.config import ecr_repo_name, settings
from multideploy.exceptions import BuildException
from multideploy.utils import docker_client, multiline_log_printer


async def build_image(repo_dir: Path, current_hash: str):
    repo_name = repo_dir.name
    logger.info(f"Building image for {repo_name}")
    logger.info(f"Working dir {repo_dir}. ls: {list(repo_dir.glob('*'))}")
    logger.info(f"IMAGE VERSION loaded from env: {settings.IMAGE_VERSION}")
    try:
        image_obj, build_log = docker_client.images.build(
            path=str(repo_dir),
            dockerfile=f"{repo_dir}/Dockerfile",
            rm=True,
            buildargs={"FUNCTION_CODE_DIR": repo_name},
            labels={settings.HASH_DOCKER_LABEL_NAME: current_hash},
            tag=f"{ecr_repo_name}/{repo_name}:{settings.IMAGE_VERSION}",
        )
        build_log = "".join([line["stream"] for line in build_log if "stream" in line])
        multiline_log_printer(repo_name, "docker build", "INFO", build_log.encode())
    except docker.errors.BuildError as err:
        logger.error(err)
        build_log = "".join(
            [line["stream"] for line in err.build_log if "stream" in line]
        )
        multiline_log_printer(repo_name, "docker build", "ERROR", build_log.encode())
        raise BuildException()

    logger.info(f"Created image with tags {image_obj.tags} for {repo_name}")
    return image_obj
