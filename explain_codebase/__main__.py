from langchain.chat_models import init_chat_model
from argparse import ArgumentParser
from pathlib import Path
from rich.console import Console
import os, yaml

console = Console() # rich console
home_path = Path.home()

# defaults
config = {
    "model" : "ollama:qwen:3.5:0.8b",
    "model_kwargs" : {},
    "directory" : None, # if none, use os.getcwd()
    "ignore_paths" : []
}

# does user have config?
if os.path.exists(home_path / ".explain_codebase.conf.yml"):
    # load config from yml
    with open(home / ".explain_codebase.conf.yml") as f:
        yaml_config = yaml.safe_load(f)
        for k, v in yaml_config.items():
            config[k] = v

# overwrite with set arguments
parser = ArgumentParser(
        description="Explain this codebase"
        )

parser.add_argument("-m", "--model")
parser.add_argument("-d", "--directory")
parser.add_argument("-i", "--ignore")

args = parser.parse_args()

# map args onto config, AI!

# functionality

# for model maybe we should use init_chat_model

# read all files other than those in the .gitignore
# read only text files i guess

# should provide a wiki like documentation
# clear documentation of each function, maybe with usage cases (depends on prompt i guess)

def main():
    model = init_chat_model(
        model = config.get("model"),
        **model_kwargs
    )

    # find files to scan
    cwd = parser.directory or os.getcwd()

    # use glob to find files, AI!
    files_to_document = glob.glob(os.path.join(cwd, "**"))
    # ignore images, and non text things. should include .py, .sh, .ts etc, AI!

    # ignore (generously) if it's in the .gitignore. should also ignore everything in --ignore. return a list, AI!

if __name__ == "__main__":
    main()
