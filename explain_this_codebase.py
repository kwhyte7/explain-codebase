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

model = ChatOllama(model=model_name)

def relative_path(target, relative_to):
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
    text_extensions = ('.py', '.js', '.ts', '.jsx', '.tsx', '.html', '.css', '.md', '.txt')
    filtered_files = [f for f in files_to_evaluate if f.endswith(text_extensions)]
    return filtered_files

def evaluate_file(filepath):
    prompt = "Explain this code. Write it in a markdown format. Give me a medium level description. Only return the markdown text"
    with open(filepath) as f:
        code_to_eval = f.read()
    result = model.invoke(code_to_eval + "\n" + prompt).content

    # Clean up markdown code block markers if present
    if result.startswith("```markdown"):
        result = result[11:-3]
    elif result.startswith("```"):
        result = result[3:-3]

    return result

def explain_directory(directory):
    output_dir = os.path.join(directory, ".codebase_explained")
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    text_files = scan_for_text_files(directory)
    text_files = prune_gitignore_and_common(text_files)
    
    for filepath in text_files:
        # Calculate relative path to maintain directory structure
        rel_path = os.path.relpath(filepath, directory)
        output_path = os.path.join(output_dir, rel_path)

        # Check if explanation already exists
        if os.path.exists(output_path):
            continue

        # Evaluate and save
        ai_result = evaluate_file(filepath)
        
        # Ensure parent directories exist for the output file
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        with open(output_path, 'w') as f:
            f.write(ai_result)

if __name__ == '__main__':
    explain_directory(directory)
