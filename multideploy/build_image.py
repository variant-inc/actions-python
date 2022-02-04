from pathlib import Path

import docker
from loguru import logger

from multideploy.exceptions import BuildException
from multideploy.utils import docker_client, multiline_log_printer, short_hash, base_dir
from multideploy.config import settings

async def build_image(repo_dir: Path, current_hash: str):
    repo_name = repo_dir.name
    logger.info(f"Building image for {repo_name}")

    # look for dockerfile in repo_dir if not found use default from .common
    common_dir = Path(base_dir) / ".common"
    docker_file_path = repo_dir
    if not (docker_file_path / "Dockerfile").exists():
        docker_file_path = common_dir

    try:
        image_obj, build_log = docker_client.images.build(
            path=str(docker_file_path.parent),
            dockerfile=f"{docker_file_path.name}/Dockerfile",
            rm=True,
            buildargs={"FUNCTION_CODE_DIR": repo_name},
            labels={"com.drivevariant.dataops.dir_hash": current_hash},
            tag=f"{settings.REPO_PREFIX}/{repo_name}:{short_hash}",
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

    return image_obj
