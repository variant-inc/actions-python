import os
from pathlib import Path

from pydantic import BaseSettings

if "DOCKER_BUILDKIT" not in os.environ:
    os.environ["DOCKER_BUILDKIT"] = "1"


class Settings(BaseSettings):
    """
    values loaded from environment variables if not present default value is used
    """

    ECR_REGISTRY_ID: str = "064859874041"
    REPO_IGNORE_DIRS: list[str] = [
        ".github",
        ".idea",
        ".git",
        ".common",
        ".pytest_cache",
        "test-actions",
        ".octopus",
    ]
    REPO_PREFIX: str = "data-ops"
    TRIVY_S3_BUCKET_NAME: str = "trivy-ops"
    BRANCH_NAME: str
    GITHUB_SHA: str
    GITHUB_REPOSITORY: str
    GITHUB_REPOSITORY_NAME_PART: str
    GITHUB_TOKEN: str

    # sonar vars
    SONAR_TOKEN: str
    SONAR_PROJECT_KEY: str
    SONAR_ORG: str

    LAZY_API_URL: str
    LAZY_API_KEY: str

    AWS_REGION: str

    HASH_DOCKER_LABEL_NAME: str = "com.drivevariant.dataops.dir_hash"
    PYZ_TEST_PACKAGE: Path = Path("/coverage.pyz")
    INPUT_MULTIREPO_SCAN_PATH: list = ["."]

    IMAGE_VERSION: str


settings = Settings()
ecr_repo_name = f"{settings.REPO_PREFIX}/{settings.GITHUB_REPOSITORY_NAME_PART}"
