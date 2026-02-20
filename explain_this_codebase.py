from glob import glob
from langchain_ollama import ChatOllama
from argparse import ArgumentParser
import os
from fnmatch import fnmatch
from rich.progress import Progress, BarColumn, TextColumn, TimeRemainingColumn
from rich.console import Console
from collections import defaultdict

parser = ArgumentParser(
        description="Explain this codebase"
        )

parser.add_argument("-m", "--model")
parser.add_argument("-d", "--directory")

args = parser.parse_args()

model_name = args.model or "qwen3:4b"
directory = args.directory or os.getcwd()

model = ChatOllama(model=model_name)

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
    prompt = "Generate a comprehensive, rich markdown explanation. You are outputting directly to a markdown file. You are the markdown file. Structure it with headers for Purpose, Key Features, Dependencies, and Usage. Keep it concise but detailed. Only return the markdown text. Do not include any introductory text."

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

    with Progress(
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        TimeRemainingColumn(),
    ) as progress:
        task_id = progress.add_task("Explaining files", total=len(text_files))
        for filepath in text_files:
            print(f"Scanning: {filepath}")

            # Calculate relative path to maintain directory structure
            rel_path = os.path.relpath(filepath, directory)
            # Change extension to .md
            output_path = os.path.join(output_dir, os.path.splitext(rel_path)[0] + '.md')

            # Check if explanation already exists
            if os.path.exists(output_path):
                continue

            # Evaluate and save
            ai_result = evaluate_file(filepath)

            # Ensure parent directories exist for the output file
            os.makedirs(os.path.dirname(output_path), exist_ok=True)

            with open(output_path, 'w') as f:
                f.write(ai_result)

            progress.update(task_id, advance=1)

def summarize_explanations(directory):
    output_dir = os.path.join(directory, ".codebase_explained")
    if not os.path.exists(output_dir):
        return

    # Collect all markdown files
    md_files = []
    for root, dirs, files in os.walk(output_dir):
        for file in files:
            if file.endswith('.md'):
                md_files.append(os.path.join(root, file))

    if not md_files:
        return

    # Helper to generate a summary for a list of files
    def create_directory_summary(file_list, output_path):
        console = Console()
        # Read contents
        file_contents = []
        for file_path in file_list:
            console.log(f"Scanning file: {file_path}")
            with open(file_path, 'r') as f:
                file_contents.append(f.read())

        combined_input = "\n\n---\n\n".join(file_contents)
        prompt = "You are summarizing the following markdown files into a single comprehensive overview for a directory. Structure it with headers for each file. Keep it concise. Only return the markdown text."

        result = model.invoke(combined_input + "\n" + prompt).content

        # Clean up markdown code block markers if present
        if result.startswith("```markdown"):
            result = result[11:-3]
        elif result.startswith("```"):
            result = result[3:-3]

        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, 'w') as f:
            f.write(result)

    # Group files by directory
    dir_groups = defaultdict(list)
    for f in md_files:
        # Get relative directory path
        rel_dir = os.path.dirname(os.path.relpath(f, output_dir))
        if rel_dir == '.':
            rel_dir = 'root'
        dir_groups[rel_dir].append(f)

    # Generate summaries for each directory
    console = Console()
    with Progress(
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        TimeRemainingColumn(),
    ) as progress:
        task_id = progress.add_task("Summarizing directories", total=len(dir_groups))
        for dir_name, files in dir_groups.items():
            console.print(f"[bold cyan]Processing directory:[/bold cyan] {dir_name}")

            if dir_name == 'root':
                # Root level files
                summary_path = os.path.join(output_dir, "OVERVIEW.md")
            else:
                summary_path = os.path.join(output_dir, dir_name, "SUMMARY.md")
            create_directory_summary(files, summary_path)

            progress.update(task_id, advance=1)

    # Generate final collated file (FULL_SUMMARY)
    if len(dir_groups) > 1:
        # Get all the summary files generated above (excluding the overview itself)
        summary_files = []
        for dir_name, files in dir_groups.items():
            if dir_name == 'root':
                continue
            summary_files.append(os.path.join(output_dir, dir_name, "SUMMARY.md"))

        if summary_files:
            create_directory_summary(summary_files, os.path.join(output_dir, "FULL_SUMMARY.md"))

if __name__ == '__main__':
    explain_directory(directory)
    summarize_explanations(directory)
