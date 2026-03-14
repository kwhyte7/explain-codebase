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
    ProgressColumn,
    TaskID
)
import os, yaml, git, enum, glob, shutil, markdown

console = Console() # rich console
home_path = Path.home()

# defaults
config = {
    "model" : "ollama:qwen:3.5:0.8b",
    "model_kwargs" : {
        "num_predict" : 5000
    },
    "directory" : None, # if none, use os.getcwd()
    "prompt" : "Write documentation for the file content above, use code snippets if applicabble, write functions and explain how they work in MD format.",
    "ignore_paths" : [],
    "html" : True
}

# sorry idk where to put this lmaooo
css_for_html = """
/* Modern markdown-inspired CSS */
:root {
  --max-width: 800px;
  --font-sans: -apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif;
  --font-mono: 'SF Mono', Monaco, 'Cascadia Code', 'Roboto Mono', monospace;
  --bg-primary: #ffffff;
  --bg-secondary: #f6f8fa;
  --text-primary: #24292e;
  --text-secondary: #57606a;
  --border-color: #d0d7de;
  --accent: #0969da;
  --accent-hover: #0a4c9e;
  --code-bg: rgba(175, 184, 193, 0.2);
  --blockquote-border: #d0d7de;
}

@media (prefers-color-scheme: dark) {
  :root {
    --bg-primary: #0d1117;
    --bg-secondary: #161b22;
    --text-primary: #c9d1d9;
    --text-secondary: #8b949e;
    --border-color: #30363d;
    --accent: #2f81f7;
    --accent-hover: #3c8eff;
    --code-bg: rgba(110, 118, 129, 0.4);
    --blockquote-border: #3b434b;
  }
}

* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: var(--font-sans);
  line-height: 1.6;
  color: var(--text-primary);
  background-color: var(--bg-primary);
  padding: 2rem 1rem;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

.container {
  max-width: var(--max-width);
  margin: 0 auto;
}

/* Typography */
h1, h2, h3, h4, h5, h6 {
  margin-top: 1.5rem;
  margin-bottom: 1rem;
  font-weight: 600;
  line-height: 1.25;
}

h1 { font-size: 2em; border-bottom: 1px solid var(--border-color); padding-bottom: 0.3em; }
h2 { font-size: 1.5em; border-bottom: 1px solid var(--border-color); padding-bottom: 0.3em; }
h3 { font-size: 1.25em; }
h4 { font-size: 1em; }
h5 { font-size: 0.875em; }
h6 { font-size: 0.85em; color: var(--text-secondary); }

p {
  margin-bottom: 1.25rem;
}

/* Links */
a {
  color: var(--accent);
  text-decoration: none;
}

a:hover {
  text-decoration: underline;
}

/* Lists */
ul, ol {
  margin-bottom: 1.25rem;
  padding-left: 2rem;
}

li {
  margin-bottom: 0.25rem;
}

li > ul,
li > ol {
  margin-bottom: 0;
  margin-top: 0.25rem;
}

/* Code */
code {
  font-family: var(--font-mono);
  font-size: 0.875em;
  padding: 0.2em 0.4em;
  background-color: var(--code-bg);
  border-radius: 6px;
}

pre {
  font-family: var(--font-mono);
  font-size: 0.875em;
  background-color: var(--bg-secondary);
  border: 1px solid var(--border-color);
  border-radius: 6px;
  padding: 1rem;
  margin-bottom: 1.25rem;
  overflow-x: auto;
}

pre code {
  background-color: transparent;
  padding: 0;
  border-radius: 0;
  font-size: inherit;
  white-space: pre;
  word-break: normal;
  word-wrap: normal;
}

/* Blockquotes */
blockquote {
  margin: 0 0 1.25rem 0;
  padding: 0 1em;
  color: var(--text-secondary);
  border-left: 0.25em solid var(--blockquote-border);
}

blockquote p {
  margin-bottom: 0.5rem;
}

blockquote p:last-child {
  margin-bottom: 0;
}

/* Tables */
table {
  width: 100%;
  margin-bottom: 1.25rem;
  border-collapse: collapse;
  border-spacing: 0;
}

th {
  font-weight: 600;
  background-color: var(--bg-secondary);
}

th,
td {
  padding: 0.5rem 1rem;
  border: 1px solid var(--border-color);
}

tr {
  background-color: var(--bg-primary);
  border-top: 1px solid var(--border-color);
}

/* Images */
img {
  max-width: 100%;
  height: auto;
  border-radius: 6px;
  border: 1px solid var(--border-color);
  margin: 1rem 0;
}

/* Horizontal rule */
hr {
  height: 0.25em;
  padding: 0;
  margin: 2rem 0;
  background-color: var(--border-color);
  border: 0;
}

/* Definition lists (for completeness) */
dt {
  font-weight: 600;
  margin-top: 0.5rem;
}

dd {
  margin-left: 2rem;
  margin-bottom: 0.5rem;
  color: var(--text-secondary);
}

/* Small text */
small {
  font-size: 0.875em;
  color: var(--text-secondary);
}

/* Keyboard input */
kbd {
  font-family: var(--font-mono);
  font-size: 0.875em;
  padding: 0.2rem 0.4rem;
  background-color: var(--bg-secondary);
  border: 1px solid var(--border-color);
  border-radius: 6px;
  box-shadow: inset 0 -1px 0 var(--border-color);
}

/* Mark/highlight */
mark {
  background-color: #fff8c5;
  padding: 0.2em 0;
  color: var(--text-primary);
}

@media (prefers-color-scheme: dark) {
  mark {
    background-color: #bb800926;
  }
}

/* Checkbox lists (for task lists) */
input[type="checkbox"] {
  margin-right: 0.5rem;
  transform: translateY(0.2rem);
}

/* Footnotes */
.footnotes {
  margin-top: 2rem;
  padding-top: 1rem;
  border-top: 1px solid var(--border-color);
  font-size: 0.875em;
  color: var(--text-secondary);
}

.footnotes li {
  margin-bottom: 0.5rem;
}

/* Print styles */
@media print {
  body {
    background-color: #fff;
    color: #000;
    padding: 0.5in;
  }

  pre, code, blockquote {
    background-color: #f5f5f5;
    border: 1px solid #ddd;
  }

  a {
    color: #000;
    text-decoration: underline;
  }

  a[href]::after {
    content: " (" attr(href) ")";
    font-size: 0.9em;
    font-weight: normal;
  }

  a[href^="#"]::after,
  a[href^="javascript:"]::after {
    content: "";
  }
}
"""


# does user have config?
if os.path.exists(home_path / ".explain_codebase.conf.yml"):
    # load config from yml
    with open(home_path / ".explain_codebase.conf.yml") as f:
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

class MediaType(enum.Enum):
    TEXT = "Text"
    PDF = "PDF"
    DOCX = "DOCX"
    DOC = "DOC"
    XLSX = "XLSX"
    XLS = "XLS"
    PPTX = "PPTX"
    PPT = "PPT"
    JPEG = "JPEG"
    PNG = "PNG"
    GIF = "GIF"
    BMP = "BMP"
    MP3 = "MP3"
    WAV = "WAV"
    MP4 = "MP4"
    AVI = "AVI"
    MKV = "MKV"
    UNKNOWN = "Unknown"

def detect_media_type(file_path: Path) -> MediaType:
    try:
        with file_path.open('rb') as file:
            initial_chunk = file.read(1024)
            if initial_chunk.startswith(b'%PDF'):
                return MediaType.PDF
            elif initial_chunk.startswith(b'PK\x03\x04'):
                return MediaType.DOCX
            elif initial_chunk.startswith(b'\xD0\xCF\x11\xE0\xA1\xB1\x1A\xE1'):
                return MediaType.DOC
            elif initial_chunk.startswith(b'\xFF\xD8\xFF'):
                return MediaType.JPEG
            elif initial_chunk.startswith(b'\x89PNG\r\n\x1A\n'):
                return MediaType.PNG
            elif initial_chunk.startswith(b'GIF89a') or initial_chunk.startswith(b'GIF87a'):
                return MediaType.GIF
            elif initial_chunk.startswith(b'BM'):
                return MediaType.BMP
            elif initial_chunk.startswith(b'RIFF') and initial_chunk[8:12] == b'WAVE':
                return MediaType.WAV
            elif initial_chunk.startswith(b'ID3') or initial_chunk[0:2] == b'\xFF\xFB':
                return MediaType.MP3
            elif initial_chunk.startswith(b'\x00\x00\x00\x18ftypmp42') or initial_chunk.startswith(b'\x00\x00\x00 ftypisom'):
                return MediaType.MP4
            elif initial_chunk.startswith(b'RIFF') and initial_chunk[8:12] == b'AVI ':
                return MediaType.AVI
            elif initial_chunk.startswith(b'\x1A\x45\xDF\xA3'):
                return MediaType.MKV
            else:
                return MediaType.UNKNOWN
    except Exception as e:
        print(f"An error occurred: {e}")
        return MediaType.UNKNOWN

def is_text_file(file_path: Path) -> tuple[bool, MediaType]:
    media_type = detect_media_type(file_path)
    if media_type != MediaType.UNKNOWN:
        return False, media_type

    try:
        with open(file_path, 'rb') as file:
            for chunk in iter(lambda: file.read(4096), b''):
                chunk.decode('utf-8')
                if any(c < 32 and c not in (9, 10, 13) for c in chunk):
                    return False, MediaType.UNKNOWN
    except UnicodeDecodeError:
        return False, MediaType.UNKNOWN
    except Exception as e:
        print(f"An error occurred: {e}")
        return False, MediaType.UNKNOWN

    return True, MediaType.TEXT


def ask_add_codebase_explained_to_gitignore(directory):
    # Check .gitignore
    gitignore_path = os.path.join(directory, '.gitignore')
    if os.path.exists(gitignore_path):
        with open(gitignore_path, 'r') as f:
            if '.codebase_explained' not in f.read():
                if Confirm.ask("Add '.codebase_explained' to .gitignore?"):
                    with open(gitignore_path, 'a') as f:
                        f.write('\n.codebase_explained\n')

def create_codebase_explained_folder(output_dir):
    # Check existing directory
    if os.path.exists(output_dir):
        if not Confirm.ask(f"Overwrite existing '.codebase_explained' directory?"):
            # If user says no, proceed but skip overwriting existing files
            return False
        else:
            shutil.rmtree(output_dir)

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    return True

def paths_for_file(filepath, cwd, output_dir):
    some_paths = [
        os.path.basename(filepath).replace(".", "_"),
        os.path.relpath(filepath, cwd)
    ]

    some_paths.append(
        os.path.join(os.path.join(cwd, ".codebase_explained"), os.path.dirname(some_paths[1]))
    )

    some_paths.append(
        os.path.join(some_paths[2], some_paths[0]) + (config.get("html") and ".html" or ".md")
    )

    return some_paths

def document_file(model, filepath, cwd, output_dir):
    with open(filepath) as f:
        content = f.read()

    # ask the model
    result = model.invoke(f"{content}\n\n{config.get('prompt')}").content

    # now need to get relpath, and save it.
    [filename, relative_path, new_dirpath, new_filepath] = paths_for_file(filepath, cwd, output_dir)
    os.makedirs(new_dirpath, exist_ok=True)

    with open(new_filepath, "w") as f:
        if config.get("html"):
            f.write("<html><head><style>" + css_for_html + "</style></head><body>" + markdown.markdown(result) + "</body></html>")
        else:
            f.write(result)

    return

def map_display_name_to_href_element(content):
    return f"<li><a href='{content['relative_path']}'>{content['display_name']}</a></li>"

def main():
    console.print(f"[#00FF00]Using model[/#00FF00] {config.get('model')}")
    model = init_chat_model(
        model = config.get("model"),
        **config.get("model_kwargs")
    )

    # find files to scan
    cwd = args.directory or os.getcwd()

    # use glob to find files
    files_to_document = glob.glob(os.path.join(cwd, "**/*.*"), recursive=True)
    # filter by if its ignored by git, or is text file
    files_to_document = [filepath for filepath in files_to_document if is_text_file(Path(filepath)) and not is_git_ignored_gitpython(filepath)]

    # for each file, read it, summarise it and save it to cwd + .codebase_explained

    ask_add_codebase_explained_to_gitignore(cwd)

    output_dir = os.path.join(cwd, ".codebase_explained")

    overwriting = create_codebase_explained_folder(output_dir)

    number_of_files_to_document = len(files_to_document)

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
        task = progress.add_task("[green]documenting...", total=number_of_files_to_document)

        contents = []

        for filepath in files_to_document:

            [filename, relative_path, new_dirpath, new_filepath] = paths_for_file(filepath, cwd, output_dir)

            contents.append({
                "relative_path" : os.path.relpath(new_filepath, output_dir),
                "display_name" : os.path.relpath(filepath, cwd)
            })

            if os.path.exists(filepath) and not overwriting:
                console.log(f"Skipping {filepath} as it already exists.")
                progress.update(task, advance=1)
                continue

            console.log(f"Documenting {filepath}")
            document_file(model, filepath, cwd, output_dir)
            progress.update(task, advance=1)

        console.log(f"Writing contents page....")
        with open(os.path.join(output_dir, "index.html"), "w") as f:
            contents_html = "<html><head><style>" + css_for_html + "</style></head><body><h1>.codebase_explained</h1><ul>" + "\n".join(list(map(map_display_name_to_href_element, contents))) + "</ul></body></html>"
            f.write(contents_html)


if __name__ == "__main__":
    main()
