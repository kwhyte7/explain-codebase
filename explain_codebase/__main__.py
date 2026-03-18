from langchain.chat_models import init_chat_model
from argparse import ArgumentParser
from pathlib import Path
from rich.console import Console
from rich.prompt import Confirm
from rich.progress import (
    Progress,
    SpinnerColumn,
    BarColumn,
    TextColumn,
    TimeRemainingColumn,
    TimeElapsedColumn,
)
import os, yaml, git, enum, glob, shutil, markdown
from explain_codebase.styles import Styles
from explain_codebase.remote_repository import get_remote_repo_files
from explain_codebase.local_repository import (
    is_text_file,
    is_git_ignored_gitpython,
    ask_add_output_to_gitignore,
)
import asyncio

console = Console()  # rich console
home_path = Path.home()


# defaultsp
config = {
    "model": "ollama:qwen3.5:0.8b",
    "model_kwargs": {"num_predict": 5000},
    "directory": None,  # if none, use os.getcwd()
    "prompt": "Write documentation for the file content above, use code snippets if applicable, write functions and explain how they work in MD format.",
    "ignore_paths": [],
    "html": True,
}

if os.path.exists(home_path / ".explain_codebase.conf.yml"):
    # load config from yml
    with open(home_path / ".explain_codebase.conf.yml") as f:
        yaml_config = yaml.safe_load(f)
        for k, v in yaml_config.items():
            config[k] = v

# overwrite with set arguments
parser = ArgumentParser(description="Explain this codebase")

parser.add_argument("-m", "--model")
parser.add_argument("-d", "--directory")
parser.add_argument("-i", "--ignore")
parser.add_argument("-r", "--repository")

args = parser.parse_args()


def create_output_folder(output_dir):
    # Check existing directory
    if os.path.exists(output_dir):
        if not Confirm.ask(f"Overwrite existing '.output' directory?"):
            # If user says no, proceed but skip overwriting existing files
            return False
        else:
            shutil.rmtree(output_dir)

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    return True


def paths_for_file(filepath, cwd, output_dir):
    if os.path.isabs(filepath):
        relative_path = os.path.relpath(filepath, cwd)
    else:
        relative_path = filepath

    some_paths = [
        os.path.basename(filepath).replace(".", "_"),
        relative_path,
    ]

    some_paths.append(
        os.path.join(os.path.join(cwd, ".output"), os.path.dirname(some_paths[1]))
    )

    some_paths.append(
        os.path.join(some_paths[2], some_paths[0])
        + (config.get("html") and ".html" or ".md")
    )

    return some_paths


async def document_file(model, filepath, cwd, output_dir, content=None):
    if content is None:
        with open(filepath) as f:
            content = f.read()

    # ask the model

    result = (await model.ainvoke(f"{content}\n\n{config.get('prompt')}")).content

    # now need to get relpath, and save it.
    [filename, relative_path, new_dirpath, new_filepath] = paths_for_file(
        filepath, cwd, output_dir
    )
    os.makedirs(new_dirpath, exist_ok=True)

    with open(new_filepath, "w") as f:
        if config.get("html"):
            f.write(
                "<html><head><style>"
                + Styles.BASE
                + "</style></head><body>"
                + markdown.markdown(result)
                + "</body></html>"
            )
        else:
            f.write(result)


def map_display_name_to_href_element(content):
    return (
        f"<li><a href='{content['relative_path']}'>{content['display_name']}</a></li>"
    )


async def main():
    console.print(f"[#00FF00]Using model[/#00FF00] {config.get('model')}")
    model = init_chat_model(
        model=args.model or config.get("model"), **config.get("model_kwargs")
    )

    # find files to scan
    cwd = args.directory or os.getcwd()

    if not args.repository:
        # use glob to find files
        files_to_document = glob.glob(os.path.join(cwd, "**/*.*"), recursive=True)
        # filter by if its ignored by git, or is text file
        files_to_document = [
            filepath
            for filepath in files_to_document
            if is_text_file(Path(filepath)) and not is_git_ignored_gitpython(filepath)
        ]

        contents_to_document = None
    else:
        files = get_remote_repo_files(args.repository)
        files_to_document = [file["path"] for file in files]
        contents_to_document = [file["text"] for file in files]

    # for each file, read it, summarise it and save it to cwd + .output

    ask_add_output_to_gitignore(cwd)

    output_dir = os.path.join(cwd, ".output")

    overwriting = create_output_folder(output_dir)

    number_of_files_to_document = len(files_to_document)

    semaphore = asyncio.Semaphore(4)

    contents = []

    # processes a file and documents it
    async def process_file(i, filepath):
        async with semaphore:
            try:
                filename, relative_path, new_dirpath, new_filepath = paths_for_file(
                    filepath, cwd, output_dir
                )

                contents.append(
                    {
                        "relative_path": os.path.relpath(new_filepath, output_dir),
                        "display_name": (
                            filepath
                            if args.repository
                            else os.path.relpath(filepath, cwd)
                        ),
                    }
                )

                if os.path.exists(filepath) and not overwriting:
                    console.log(f"Skipping {filepath} as it already exists.")
                    return

                console.log(f"Documenting {filepath}")

                if contents_to_document:
                    await document_file(
                        model, filepath, cwd, output_dir, contents_to_document[i]
                    )
                else:
                    await document_file(model, filepath, cwd, output_dir)
            except Exception as e:
                console.log(f"[red]Error:[/red] {filepath} -> {e}")

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        TimeRemainingColumn(),
        TimeElapsedColumn(),
        console=console,
        transient=True,
    ) as progress:
        task = progress.add_task(
            "[green]documenting...", total=number_of_files_to_document
        )

        # all documenting happens here
        async def wrapped(i, f):
            await process_file(i, f)
            progress.update(task, advance=1)

        await asyncio.gather(*(wrapped(i, f) for i, f in enumerate(files_to_document)))

        # making index.html
        console.log(f"Writing contents page....")
        with open(os.path.join(output_dir, "index.html"), "w") as f:
            contents_html = (
                "<html><head><style>"
                + Styles.BASE
                + "</style></head><body><h1>.output</h1><ul>"
                + "\n".join(list(map(map_display_name_to_href_element, contents)))
                + "</ul></body></html>"
            )
            f.write(contents_html)


if __name__ == "__main__":
    asyncio.run(main())
