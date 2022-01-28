import os
from typing import List

from pydantic import BaseSettings

if not "DOCKER_BUILDKIT" in os.environ:
    os.environ["DOCKER_BUILDKIT"] = "1"

class Settings(BaseSettings):
    """
    values loaded from environment variables if not present default value is used
    """

    ECR_REGISTRY_ID: str = "064859874041"
    REPO_IGNORE_DIRS: List[str] = [".github", ".idea", ".git", ".common", ".pytest_cache"]
    REPO_PREFIX: str = "data-ops"

settings = Settings()
