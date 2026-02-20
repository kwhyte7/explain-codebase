from glob import glob
from langchain_ollama import ChatOllama
from argparse import ArgumentParser
import os
from fnmatch import fnmatch

parser = ArgumentParser(
        description="Explain this codebase"  
        )

parser.add_argument("-m", "--model")
parser.add_argument("-d", "--directory")

args = parser.parse_args()

model = args.model or "qwen3:4b"
directory = args.directory = os.getcwd()

def relative_path(target, relative_to): # this could be improved, AI!
    return os.path.relpath(target, relative_to)

# read gitignore, then ignore matching files
def prune_gitignore_and_common(files_list: list) -> list:
    # list[str]
    
    # I want this function to: read .gitignore, prune those files (also prune hidden files/folders), AI!

    gitignore_path = os.path.join(os.getcwd(), '.gitignore')
    if not os.path.exists(gitignore_path):
        gitignore_path = os.path.expanduser('~/.gitignore_global')

    ignored_patterns = []
    if os.path.exists(gitignore_path):
        with open(gitignore_path, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    ignored_patterns.append(line)

    result = []
    for file_path in files_list:
        filename = os.path.basename(file_path)
        # Prune hidden files/folders
        if filename.startswith('.'):
            continue
        # Prune gitignore patterns
        if any(fnmatch(filename, pattern) for pattern in ignored_patterns):
            continue
        result.append(file_path)
    return result

# scan for files
def scan_for_text_files(directory="./"):
    files_to_evaluate = glob(os.path.join(directory, "**", "*"), recursive=True)
    # accept .py, .js, ETC AI!
    text_extensions = ('.py', '.js', '.ts', '.jsx', '.tsx', '.html', '.css', '.txt')
    filtered_files = [f for f in files_to_evaluate if f.endswith(text_extensions)]
    return prune_gitignore_and_common(filtered_files)

if __name__ == '__main__':
    files = scan_for_text_files(directory)
    print(f"Found {len(files)} files to evaluate.")
    print(files)
