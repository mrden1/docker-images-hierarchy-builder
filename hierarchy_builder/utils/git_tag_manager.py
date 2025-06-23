import semver
import subprocess

from hierarchy_builder.utils.logger import logger


def get_local_git_tags(image: str) -> list:
    try:
        # Run git command to get all local tags
        result = subprocess.run(
            ['git', 'tag', '-l'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=True
        )
        tags = result.stdout.splitlines()
    except subprocess.CalledProcessError as e:
        logger.error(f"Error getting git tags: {e.stderr}")
    except FileNotFoundError:
        logger.error("Git command not found. Make sure Git is installed.")
    image_tags = []
    for tag in tags:
        if image in tag:
            image_tags.append(tag.split("@")[0])
    return image_tags


def get_last_tag(tags: list) -> str:
    latest_tag = max(tags, key=lambda x: tuple(map(int, x.split('.'))))
    return latest_tag


def add_git_tag(tag: str, type: str):
    if type == "local":
        cmd = f"git tag {tag}"
    elif type == "remote":
        cmd = f"git push origin {tag}"
    else:
        logger.error("Tag type should be local or remote")
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=True
        )
        return True
    except subprocess.CalledProcessError as e:
        return f"Error: {e.stderr.strip()}"


def bump_version(tag: str, bump_type: str) -> semver.version.Version:
    ver = semver.Version.parse(tag)
    version = eval(f"ver.bump_{bump_type}()")
    return version
