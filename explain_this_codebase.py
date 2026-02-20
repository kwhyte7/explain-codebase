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

model_name = args.model or "qwen3:4b"
directory = args.directory = os.getcwd()

model = ChatOllama(model=model_name) # should have more args.. but whatever am i right

def relative_path(target, relative_to): # this could be improved, AI!
    return os.path.relpath(target, relative_to)

# read gitignore, then ignore matching files
def prune_gitignore_and_common(files_list: list) -> list:
    gitignore_path = os.path.join(directory, '.gitignore')
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
    text_extensions = ('.py', '.js', '.ts', '.jsx', '.tsx', '.html', '.css', '.txt')
    filtered_files = [f for f in files_to_evaluate if f.endswith(text_extensions)]
    return filtered_files

def evaluate_file(filepath): # shit 
    
    prompt = "Explain this code. Write it in a markdown format. Give me a medium level description. Only return the markdown text"
    with open(filepath) as f: code_to_eval = f.read()
    result = model.invoke(code_to_eval + "\n" + prompt).content

    result = (result.startswith("```markdown") and result[11:-3]) or result

    return result

def explain_directory(directory):
    text_files = scan_for_text_files(directory)
    text_files = prune_gitignore_and_common(text_files)
    
    # ok now for each file, we should
    for filepath in text_files:
        if os.path.exists(os.path.join(directory, ".codebase_explained")):
            # try to find the file in this (this should be a filestructure identical to the cwd), if it does, skip this file, AI!

        # if not, save evaluate it and save the filepath in directory/.codebase_explained, same filestructure, AI!
        ai_result = evaluate_file(filepath)

        
if __name__ == '__main__':
    files = scan_for_text_files(directory)
    print(f"Found {len(files)} files to evaluate.")
    print(files)
