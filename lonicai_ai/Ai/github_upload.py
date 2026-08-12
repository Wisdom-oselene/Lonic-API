import os
from pathlib import Path

from dotenv import load_dotenv
from github import Github


# ==========================================
# LOAD ENVIRONMENT
# ==========================================

load_dotenv()


GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
GITHUB_OWNER = os.getenv("GITHUB_OWNER")
GITHUB_REPO = os.getenv("GITHUB_REPO")


if not GITHUB_TOKEN:
    raise RuntimeError("GITHUB_TOKEN is missing from .env")

if not GITHUB_OWNER:
    raise RuntimeError("GITHUB_OWNER is missing from .env")

if not GITHUB_REPO:
    raise RuntimeError("GITHUB_REPO is missing from .env")


# ==========================================
# CONNECT TO GITHUB
# ==========================================

github = Github(GITHUB_TOKEN)

repo = github.get_repo(
    f"{GITHUB_OWNER}/{GITHUB_REPO}"
)


# ==========================================
# UPLOAD IMAGE
# ==========================================

def upload_image(
    image_path: str,
    github_path: str,
    commit_message: str = "Add training image",
):

    image_path = Path(image_path)

    if not image_path.exists():
        raise FileNotFoundError(
            f"Image not found: {image_path}"
        )

    with open(image_path, "rb") as f:
        image_data = f.read()

    try:
        existing = repo.get_contents(github_path)

        repo.update_file(
            existing.path,
            commit_message,
            image_data,
            existing.sha,
        )

    except Exception:

        repo.create_file(
            github_path,
            commit_message,
            image_data,
        )

    return {
        "success": True,
        "path": github_path,
    }