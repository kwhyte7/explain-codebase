class Styles:
    BASE = """
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
