import git, os, shutil
from pathlib import Path
from rich.prompt import Confirm


def is_git_ignored_gitpython(file_path):
    """
    Check if a file is ignored using GitPython
    """
    try:
        # Find the git repository containing the file
        repo = git.Repo(Path(file_path).parent, search_parent_directories=True)

        # Check if file is ignored
        return repo.ignored(file_path) != []
    except (git.InvalidGitRepositoryError, git.NoSuchPathError):
        # Not in a git repository
        return False


# we're only working with text files
def is_text_file(path: Path) -> bool:
    try:
        with open(path, "r", encoding="utf-8") as f:
            f.read()
        return True
    except:
        return False


def ask_add_output_to_gitignore(directory):
    # Check .gitignore
    gitignore_path = os.path.join(directory, ".gitignore")
    if os.path.exists(gitignore_path):
        with open(gitignore_path, "r") as f:
            if ".output" not in f.read():
                if Confirm.ask("Add '.output' to .gitignore?"):
                    with open(gitignore_path, "a") as f:
                        f.write("\n.output\n")
