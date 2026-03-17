import requests, zipfile, io
from pathspec import PathSpec
from urllib.parse import urlparse


def get_remote_repo_files(repo_url):
    path = urlparse(repo_url).path.strip("/")
    owner, repo = path.split("/")[:2]

    # we need a branch name to download everything
    repo_info = requests.get(f"https://api.github.com/repos/{owner}/{repo}").json()
    branch = repo_info["default_branch"]

    # downloading repository archive
    zip_url = f"https://github.com/{owner}/{repo}/archive/refs/heads/{branch}.zip"
    response = requests.get(zip_url)

    zip_file = zipfile.ZipFile(io.BytesIO(response.content))

    root = zip_file.namelist()[0]

    gitignore = None
    try:
        ignore_data = zip_file.read(root + ".gitignore").decode()
        gitignore = PathSpec.from_lines("gitwildmatch", ignore_data.splitlines())
    except:
        pass

    repo_files = []

    for path in zip_file.namelist():

        if path.endswith("/"):
            continue

        relative_path = path[len(root) :]

        if relative_path == "":
            continue

        if gitignore and gitignore.match_file(relative_path):
            continue

        data = zip_file.read(path)

        try:
            text = data.decode("utf-8")
        except:
            continue

        repo_files.append({"path": relative_path, "text": text})

    return repo_files
