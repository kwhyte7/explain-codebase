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

print(model, directory)

# read gitignore, then ignore matching files

# argv is model, directory

# scan for files
def scan_for_files(directory="./"):
    pass

# use glob for tree

# ignore hidden files

