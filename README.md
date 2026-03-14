To build this into a CLI tool that you can invoke with `python -m explain_codebase`, you need to follow a specific directory structure and configure your `pyproject.toml` to create an entry point.

Here is the step-by-step guide.

### Step 1: Clone this repo
```
git clone https://github.com/kwhyte7/explain-codebase.git
```

### Step 2: Install model provider
By default, this tool uses ollama, however you can use other providers.

#### Ensure Ollama is installed on your system - this uses ollama by default
[Here is the link to download ollama,](https://ollama.com/download) follow the download instructions and ensure that it's running on port 11434.
Download a model (example qwen3.5:0.8b) by doing
```
ollama pull qwen3.5:0.8b
```
in your terminal.

#### If you aren't using ollama
Change directory into the cloned repo.
Install your chosen provider using `uv add langchain[provider]`
Add your API keys in ~/.explain_codebase.conf.yml, under model_kwargs. Should look something like:
```yml
model: provider:model-alias # example openai:gpt-5
model_kwargs:
  - api_key: your-api-key
```

### Step 3: Install in Editable Mode
To test the tool immediately without uploading it to PyPI, install your project in "editable" (dev) mode:
```bash
pip install -e .
```

### Step 4: Run the Tool
Now, anywhere in your terminal, you can run:
```bash
python -m explain_codebase
```
This will start the program, and you should see a `.codebase_explained` directory appear.

### Step 5: View the generated documentation
Once it's been generated, you can either view the documentation files raw with a webbrowser, or you can run
```
python -m http.server 3000
```
to start a webserver, and you can view it at http://localhost:3000/

### Summary of how it works:
1.  **`[project.scripts]`**: Defines the CLI command. We named it `explain_codebase`.
2.  **`explain_codebase.__main__:main`**: Python looks for a file named `__main__.py` inside the package `explain_codebase` and runs the function called `main`.
3.  **`python -m`**: Tells Python to execute the module `explain_codebase` using the entry point we defined above.
=======

