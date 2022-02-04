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
    REPO_IGNORE_DIRS: List[str] = [
        ".github",
        ".idea",
        ".git",
        ".common",
        ".pytest_cache",
        "test-actions",
    ]
    REPO_PREFIX: str = "data-ops"
    TRIVY_S3_BUCKET_NAME: str = "trivy-ops"
    BRANCH_NAME: str
    GITHUB_SHA: str 
    
    # sonar vars
    SONAR_TOKEN: str
    SONAR_PROJECT_KEY: str
    SONAR_ORG: str

    LAZY_API_URL: str
    LAZY_API_KEY: str

    AWS_REGION: str

settings = Settings()
