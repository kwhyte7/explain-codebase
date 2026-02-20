from glob import glob
from langchain_ollama import ChatOllama
from argparse import ArgumentParser
import os

parser = ArgumentParser(
        description="Explain this codebase"  
        )

parser.add_argument("-m", "--model")
parser.add_argument("-d", "--directory")

args = parser.parse_args()

model = args.model or "qwen3:4b"
directory = args.directory = os.getcwd()

def relative_path(target, relative_to): # this could be improved, AI!
    return target.replace(relative_to, "")

# read gitignore, then ignore matching files
def prune_gitignore_and_common(files_list: list)
    # list[str]
    
    # I want this function to: read .gitignore, prune those files (also prune hidden files/folders), AI!

# scan for files
def scan_for_text_files(directory="./"):
    files_to_evaluate = glob(os.path.join(directory, "*"))
    # accept .py, .js, ETC AI!
    
    return tree_to_evaluate(files_to_evaluate)
    
