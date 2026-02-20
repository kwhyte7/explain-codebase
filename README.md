# Explain Codebase

A utility script to automatically generate comprehensive documentation for your codebase using local Large Language Models (LLMs).

This tool scans your project directory, identifies relevant text files (code, markdown, etc.), and uses a configured LLM to generate detailed markdown explanations for each file. It also creates directory-level summaries and a global overview to help you navigate and understand your project quickly.

## Features

*   **Automated Documentation:** Generates rich markdown explanations for source files.
*   **Local Execution:** Runs entirely on your machine using Ollama and LangChain (no data sent to external APIs).
*   **Intelligent Scanning:** Ignores hidden files, directories, and patterns defined in your `.gitignore` or global gitignore.
*   **Preserved Structure:** Maintains the original file/folder hierarchy in the generated documentation output.
*   **Directory Summaries:** Automatically creates `SUMMARY.md` files for each subdirectory and a global `FULL_SUMMARY.md`.
*   **Configurable:** Supports a configuration file for model settings and CLI arguments for one-off usage.

## Prerequisites

1.  **Python:** Installed on your system.
2.  **Ollama:** Installed and running locally. You need to pull the model you wish to use (e.g., `qwen3:4b`, `llama3:8b`, `codellama:7b`).

    ```bash
    ollama pull qwen3:4b
    ```

3.  **Dependencies:** Install the required Python libraries.

    ```bash
    pip install langchain-ollama rich pyyaml
    ```

## Configuration

You can configure the default model used by the script by creating a YAML configuration file in your home directory.

**File Path:** `~/.explain_codebase.conf.yml`

**Example:**
```yaml
model: "qwen3:4b"
