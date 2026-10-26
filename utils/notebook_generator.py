#!/usr/bin/env python3
"""
Notebook Generator v3.0 — Minimal & Focused

Shows only what matters:
1. Setup (requirements, paths)
2. Source code (the actual code!)
3. Entry point execution
4. Summary

No noise. No CS analysis clutter. Just the code.
"""

import argparse
import ast
import base64
import json
import os
import re
import sys
import textwrap
from collections import OrderedDict, defaultdict
from datetime import datetime
from pathlib import Path
from typing import Any


class CodeAnalyzer(ast.NodeVisitor):
    """Minimal AST analysis — only what's needed."""

    def __init__(self, filepath: str, source: str):
        self.filepath = filepath
        self.source = source
        self.line_count = len(source.splitlines())
        self.imports = []
        self.functions = []
        self.classes = []
        self.has_main_guard = False
        self.has_main_function = False
        self.external_imports = set()
        self.local_imports = set()
        self.stdlib_imports = set()

    def analyze(self) -> dict[str, Any]:
        """Run minimal analysis."""
        try:
            tree = ast.parse(self.source, filename=self.filepath)
        except SyntaxError as e:
            return self._error_result(f"SyntaxError: {e}")

        self.visit(tree)
        self._detect_main_guard(tree)

        return {
            "filepath": self.filepath,
            "source": self.source,
            "imports": self.imports,
            "functions": self.functions,
            "classes": self.classes,
            "has_main_guard": self.has_main_guard,
            "has_main_function": self.has_main_function,
            "external_imports": self.external_imports,
            "local_imports": self.local_imports,
            "stdlib_imports": self.stdlib_imports,
            "line_count": self.line_count,
        }

    def _error_result(self, error: str) -> dict[str, Any]:
        return {
            "filepath": self.filepath,
            "error": error,
            "source": self.source,
            "imports": [],
            "functions": [],
            "classes": [],
            "has_main_guard": False,
            "has_main_function": False,
            "external_imports": set(),
            "local_imports": set(),
            "stdlib_imports": set(),
            "line_count": self.line_count,
        }

    def visit_Import(self, node: ast.Import):
        for alias in node.names:
            self.imports.append(
                {"type": "import", "module": alias.name, "alias": alias.asname}
            )
            self._classify_import(alias.name.split(".")[0])
        self.generic_visit(node)

    def visit_ImportFrom(self, node: ast.ImportFrom):
        module = node.module or ""
        for alias in node.names:
            self.imports.append(
                {
                    "type": "from",
                    "module": module,
                    "name": alias.name,
                    "alias": alias.asname,
                }
            )
        if module:
            self._classify_import(module.split(".")[0])
        self.generic_visit(node)

    def visit_FunctionDef(self, node: ast.FunctionDef):
        if node.name == "main":
            self.has_main_function = True
        self.functions.append(
            {
                "name": node.name,
                "line": node.lineno,
                "end_line": getattr(node, "end_lineno", node.lineno),
            }
        )
        self.generic_visit(node)

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef):
        if node.name == "main":
            self.has_main_function = True
        self.functions.append(
            {
                "name": node.name,
                "line": node.lineno,
                "end_line": getattr(node, "end_lineno", node.lineno),
                "is_async": True,
            }
        )
        self.generic_visit(node)

    def visit_ClassDef(self, node: ast.ClassDef):
        self.classes.append(
            {
                "name": node.name,
                "line": node.lineno,
                "end_line": getattr(node, "end_lineno", node.lineno),
            }
        )
        self.generic_visit(node)

    def _detect_main_guard(self, tree: ast.Module):
        """Detect if __name__ == '__main__':"""
        for node in tree.body:
            if isinstance(node, ast.If):
                test = node.test
                if isinstance(test, ast.Compare):
                    if isinstance(test.left, ast.Name) and test.left.id == "__name__":
                        if len(test.ops) == 1 and isinstance(test.ops[0], ast.Eq):
                            if isinstance(test.comparators[0], ast.Constant):
                                if test.comparators[0].value == "__main__":
                                    self.has_main_guard = True
                                    return

    def _classify_import(self, module_name: str):
        """Classify imports as stdlib, external, or local."""
        STDLIB = {
            "abc",
            "argparse",
            "array",
            "ast",
            "asyncio",
            "atexit",
            "base64",
            "bisect",
            "builtins",
            "bz2",
            "calendar",
            "cmath",
            "cmd",
            "code",
            "codecs",
            "collections",
            "colorsys",
            "compileall",
            "concurrent",
            "configparser",
            "contextlib",
            "contextvars",
            "copy",
            "copyreg",
            "cProfile",
            "csv",
            "ctypes",
            "curses",
            "dataclasses",
            "datetime",
            "dbm",
            "decimal",
            "difflib",
            "dis",
            "distutils",
            "doctest",
            "email",
            "encodings",
            "enum",
            "errno",
            "faulthandler",
            "fcntl",
            "filecmp",
            "fileinput",
            "fnmatch",
            "fractions",
            "ftplib",
            "functools",
            "gc",
            "getopt",
            "getpass",
            "gettext",
            "glob",
            "grp",
            "gzip",
            "hashlib",
            "heapq",
            "hmac",
            "html",
            "http",
            "idlelib",
            "imaplib",
            "imp",
            "importlib",
            "inspect",
            "io",
            "ipaddress",
            "itertools",
            "json",
            "keyword",
            "lib2to3",
            "linecache",
            "locale",
            "logging",
            "lzma",
            "mailbox",
            "marshal",
            "math",
            "mimetypes",
            "mmap",
            "modulefinder",
            "multiprocessing",
            "netrc",
            "numbers",
            "operator",
            "optparse",
            "os",
            "parser",
            "pathlib",
            "pdb",
            "pickle",
            "pickletools",
            "pipes",
            "pkgutil",
            "platform",
            "plistlib",
            "poplib",
            "posix",
            "posixpath",
            "pprint",
            "profile",
            "pstats",
            "pty",
            "pwd",
            "py_compile",
            "pyclbr",
            "pydoc",
            "queue",
            "quopri",
            "random",
            "re",
            "readline",
            "reprlib",
            "resource",
            "rlcompleter",
            "runpy",
            "sched",
            "secrets",
            "select",
            "selectors",
            "shelve",
            "shlex",
            "shutil",
            "signal",
            "site",
            "smtplib",
            "sndhdr",
            "socket",
            "socketserver",
            "sqlite3",
            "ssl",
            "stat",
            "statistics",
            "string",
            "stringprep",
            "struct",
            "subprocess",
            "symtable",
            "sys",
            "sysconfig",
            "syslog",
            "tabnanny",
            "tarfile",
            "telnetlib",
            "tempfile",
            "termios",
            "test",
            "textwrap",
            "threading",
            "time",
            "timeit",
            "tkinter",
            "token",
            "tokenize",
            "tomllib",
            "trace",
            "traceback",
            "tracemalloc",
            "tty",
            "turtle",
            "types",
            "typing",
            "unicodedata",
            "unittest",
            "urllib",
            "uu",
            "uuid",
            "venv",
            "warnings",
            "wave",
            "weakref",
            "webbrowser",
            "winreg",
            "winsound",
            "wsgiref",
            "xml",
            "xmlrpc",
            "zipapp",
            "zipfile",
            "zipimport",
            "zlib",
            "_thread",
            "__future__",
        }
        if module_name in STDLIB or module_name.startswith("_"):
            self.stdlib_imports.add(module_name)
        elif module_name in (".", ""):
            self.local_imports.add(module_name)
        else:
            self.external_imports.add(module_name)


class ProjectScanner:
    """Scans project and builds minimal analysis."""

    DEFAULT_EXCLUDE = {
        "venv",
        ".venv",
        "env",
        ".env",
        "node_modules",
        "__pycache__",
        ".git",
        ".hg",
        ".svn",
        ".tox",
        ".nox",
        ".mypy_cache",
        ".pytest_cache",
        ".ruff_cache",
        "dist",
        "build",
        "egg-info",
        ".eggs",
        ".idea",
        ".vscode",
        "site-packages",
        ".arena",
        ".cache",
        "coverage",
        ".next",
        ".nuxt",
        ".output",
        ".parcel-cache",
        ".svelte-kit",
        ".turbo",
        ".vite",
        "notebook_generator.py",
        "html_visualizer.py",
        "via_negativa_features.py",
    }

    def __init__(self, project_dir: str, exclude_patterns: list[str] = None):
        self.project_dir = Path(project_dir).resolve()
        self.exclude_patterns = set(exclude_patterns or [])
        self.exclude_patterns.update(self.DEFAULT_EXCLUDE)
        self.files = OrderedDict()
        self.dependency_graph = defaultdict(set)
        self.execution_order = []
        self.entry_points = []
        self.requirements = []
        self.project_name = self.project_dir.name

    def scan(self) -> dict[str, Any]:
        """Scan project."""
        print(f"\n{'=' * 70}")
        print("  🚀 Notebook Generator v3.0 — Minimal & Focused")
        print(f"{'=' * 70}")
        print(f"\n  📁 Project: {self.project_dir}")
        print("  🔍 Scanning...\n")

        py_files = self._find_python_files()
        print(f"  📄 Found {len(py_files)} Python files\n")

        if not py_files:
            print("  ⚠️  No Python files found!")
            sys.exit(1)

        # Analyze files
        for filepath in sorted(py_files):
            rel_path = str(Path(filepath).relative_to(self.project_dir))
            try:
                with open(filepath, "r", encoding="utf-8", errors="replace") as f:
                    source = f.read()
                analyzer = CodeAnalyzer(filepath, source)
                analysis = analyzer.analyze()
                self.files[rel_path] = analysis
            except Exception as e:
                print(f"  ⚠️  Error: {rel_path}: {e}")
                self.files[rel_path] = CodeAnalyzer(filepath, "")._error_result(str(e))

        # Build dependency graph and execution order
        self._resolve_imports()
        self._build_dependency_graph()
        self._topological_sort()
        self._detect_entry_points()
        self._detect_requirements()

        self._print_summary()

        return {
            "files": self.files,
            "execution_order": self.execution_order,
            "entry_points": self.entry_points,
            "requirements": self.requirements,
            "dependency_graph": dict(self.dependency_graph),
            "project_name": self.project_name,
            "project_dir": str(self.project_dir),
        }

    def _find_python_files(self) -> list[str]:
        """Find all .py files."""
        py_files = []
        for root, dirs, files in os.walk(self.project_dir):
            dirs[:] = [
                d
                for d in dirs
                if d not in self.exclude_patterns
                and not d.startswith(".")
                and d != "__pycache__"
            ]
            for f in files:
                if f.endswith(".py"):
                    filepath = os.path.join(root, f)
                    rel_path = str(Path(filepath).relative_to(self.project_dir))
                    skip = any(p in rel_path or p in f for p in self.exclude_patterns)
                    if not skip:
                        py_files.append(filepath)
        return py_files

    def _resolve_imports(self):
        """Classify imports."""
        project_modules = set()
        for rel_path in self.files:
            module_name = rel_path.replace(os.sep, "/").replace("/", ".")
            module_name = module_name.removesuffix(".py")
            module_name = module_name.removesuffix(".__init__")
            project_modules.add(module_name)
            project_modules.add(module_name.split(".")[0])

        for rel_path, analysis in self.files.items():
            external = analysis.get("external_imports", set())
            resolved_ext = set()
            resolved_loc = set()
            for mod in external:
                if mod in project_modules:
                    resolved_loc.add(mod)
                else:
                    resolved_ext.add(mod)
            analysis["external_imports"] = resolved_ext
            analysis["local_imports"] = (
                analysis.get("local_imports", set()) | resolved_loc
            )

    def _build_dependency_graph(self):
        """Build dependency graph."""
        module_to_file = {}
        for rel_path in self.files:
            module_name = rel_path.replace(os.sep, "/").replace("/", ".")
            module_name = module_name.removesuffix(".py")
            module_name = module_name.removesuffix(".__init__")
            module_to_file[module_name] = rel_path
            module_to_file[module_name.split(".")[-1]] = rel_path

        for rel_path, analysis in self.files.items():
            for imp in analysis.get("local_imports", set()):
                dep_file = module_to_file.get(imp)
                if dep_file and dep_file != rel_path:
                    self.dependency_graph[rel_path].add(dep_file)

    def _topological_sort(self):
        """Sort files by dependencies."""
        visited = set()
        temp_mark = set()
        order = []
        all_files = set(self.files.keys())

        def visit(node):
            if node in temp_mark:
                return
            if node in visited:
                return
            temp_mark.add(node)
            for dep in self.dependency_graph.get(node, set()):
                if dep in all_files:
                    visit(dep)
            temp_mark.discard(node)
            visited.add(node)
            order.append(node)

        for f in sorted(all_files):
            if f not in visited:
                visit(f)
        self.execution_order = order

    def _detect_entry_points(self):
        """Detect entry points."""
        for rel_path, analysis in self.files.items():
            if analysis.get("has_main_guard") or analysis.get("has_main_function"):
                self.entry_points.append(rel_path)
            elif rel_path in (
                "main.py",
                "app.py",
                "run.py",
                "manage.py",
                "server.py",
                "cli.py",
                "start.py",
                "__main__.py",
            ):
                if rel_path not in self.entry_points:
                    self.entry_points.append(rel_path)

    def _detect_requirements(self):
        """Detect requirements."""
        requirements = set()
        req_file = self.project_dir / "requirements.txt"
        if req_file.exists():
            with open(req_file) as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#") and not line.startswith("-"):
                        pkg = re.split(r"[>=<!~\[]", line)[0].strip()
                        if pkg:
                            requirements.add(pkg)

        pyproject = self.project_dir / "pyproject.toml"
        if pyproject.exists():
            with open(pyproject) as f:
                content = f.read()
                match = re.search(r"dependencies\s*=\s*\[(.*?)\]", content, re.DOTALL)
                if match:
                    for dep in re.findall(r'"([^"]+)"', match.group(1)):
                        pkg = re.split(r"[>=<!~\[]", dep)[0].strip()
                        if pkg:
                            requirements.add(pkg)

        # Add external imports
        IMPORT_TO_PIP = {
            "cv2": "opencv-python",
            "PIL": "Pillow",
            "sklearn": "scikit-learn",
            "yaml": "pyyaml",
            "bs4": "beautifulsoup4",
            "dotenv": "python-dotenv",
            "jwt": "PyJWT",
            "numpy": "numpy",
            "pandas": "pandas",
            "matplotlib": "matplotlib",
            "flask": "flask",
            "django": "django",
            "fastapi": "fastapi",
            "requests": "requests",
            "torch": "torch",
            "tensorflow": "tensorflow",
            "transformers": "transformers",
        }
        for rel_path, analysis in self.files.items():
            for ext in analysis.get("external_imports", set()):
                requirements.add(IMPORT_TO_PIP.get(ext, ext))

        self.requirements = sorted(requirements)

    def _print_summary(self):
        """Print summary."""
        total_lines = sum(f.get("line_count", 0) for f in self.files.values())
        total_functions = sum(len(f.get("functions", [])) for f in self.files.values())
        total_classes = sum(len(f.get("classes", [])) for f in self.files.values())

        print(f"  {'─' * 55}")
        print("  📊 PROJECT SUMMARY")
        print(f"  {'─' * 55}")
        print(f"  📄 Python files:    {len(self.files)}")
        print(f"  📝 Total lines:     {total_lines:,}")
        print(f"  ⚡ Functions:       {total_functions}")
        print(f"  🏗️  Classes:        {total_classes}")
        print(f"  📦 Requirements:    {len(self.requirements)}")
        print(f"  🎯 Entry points:    {len(self.entry_points)}")
        print(f"  {'─' * 55}")

        if self.entry_points:
            print("\n  🎯 Entry Points:")
            for ep in self.entry_points:
                print(f"     → {ep}")

        print("\n  📋 Execution Order:")
        for i, f in enumerate(self.execution_order, 1):
            marker = " 🎯" if f in self.entry_points else ""
            print(f"     {i:>2}. {f}{marker}")

        print(f"\n  {'─' * 55}\n")


class NotebookGenerator:
    """Generates minimal, focused notebook."""

    def __init__(self, project_data: dict[str, Any]):
        self.data = project_data
        self.cells = []
        self.project_name = project_data.get("project_name", "Project")

    def generate(self, output_path: str) -> str:
        """Generate notebook."""
        print("  📓 Generating minimal notebook...\n")

        self._add_title_cell()
        self._add_setup_cell()
        self._add_requirements_cell()
        self._add_file_recreation_cell()
        self._add_source_code_cells()
        self._add_entry_point_cells()
        self._add_summary_cell()

        notebook = {
            "nbformat": 4,
            "nbformat_minor": 0,
            "metadata": {
                "colab": {
                    "provenance": [],
                    "name": f"{self.project_name}_notebook.ipynb",
                },
                "kernelspec": {"name": "python3", "display_name": "Python 3"},
                "language_info": {"name": "python", "version": "3.10.0"},
            },
            "cells": self.cells,
        }

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(notebook, f, indent=2, ensure_ascii=False, default=str)

        print(f"  ✅ Notebook saved: {output_path}")
        print(f"  📊 Total cells: {len(self.cells)}")
        print("\n  🚀 Open in Colab:")
        print("     https://colab.research.google.com/")
        print(f"\n{'=' * 70}\n")
        return output_path

    def _md_cell(self, source: str):
        """Add markdown cell."""
        self.cells.append(
            {
                "cell_type": "markdown",
                "metadata": {},
                "source": source.split("\n"),
            }
        )

    def _code_cell(self, source: str):
        """Add code cell."""
        self.cells.append(
            {
                "cell_type": "code",
                "metadata": {},
                "source": source.split("\n"),
                "execution_count": None,
                "outputs": [],
            }
        )

    def _add_title_cell(self):
        """Add title."""
        files = self.data.get("files", {})
        total_lines = sum(f.get("line_count", 0) for f in files.values())

        self._md_cell(f"""# 🚀 {self.project_name}

## Complete Project Notebook

> Generated on {datetime.now().strftime("%Y-%m-%d %H:%M")}

---

### 📊 Project Stats
- **Files:** {len(files)}
- **Lines of Code:** {total_lines:,}
- **Functions:** {sum(len(f.get("functions", [])) for f in files.values())}
- **Classes:** {sum(len(f.get("classes", [])) for f in files.values())}

---

### 📋 How to Use
1. **Runtime → Run all** to execute everything
2. Each file is shown with its full source code
3. Entry points are executed at the end with output capture

---
""")

    def _add_setup_cell(self):
        """Add setup."""
        self._md_cell("## ⚙️ Setup")
        self._code_cell(f"""# Setup environment
import os, sys, warnings
warnings.filterwarnings('ignore')

PROJECT_DIR = "/content/{self.project_name}"
os.makedirs(PROJECT_DIR, exist_ok=True)
os.chdir(PROJECT_DIR)

if PROJECT_DIR not in sys.path:
    sys.path.insert(0, PROJECT_DIR)

print("✅ Environment ready")
print(f"   Project: {{PROJECT_DIR}}")
print(f"   Python: {{sys.version.split()[0]}}")
""")

    def _add_requirements_cell(self):
        """Add requirements."""
        requirements = self.data.get("requirements", [])
        if not requirements:
            return

        self._md_cell("## 📦 Dependencies")
        req_str = ",\n    ".join(f'"{r}"' for r in requirements)
        self._code_cell(f"""# Install dependencies
requirements = [
    {req_str}
]

import subprocess
installed, failed = [], []
for pkg in requirements:
    if not pkg.strip(): continue
    try:
        r = subprocess.run([sys.executable, "-m", "pip", "install", "-q", pkg],
                          capture_output=True, text=True, timeout=120)
        (installed if r.returncode == 0 else failed).append(pkg)
    except: failed.append(pkg)

print(f"✅ Installed: {{len(installed)}} packages")
if failed: print(f"⚠️  Failed: {{failed}}")
""")

    def _add_file_recreation_cell(self):
        """Recreate files using base64."""
        files = self.data.get("files", {})
        self._md_cell("""## 📁 Project Files

All project files are embedded below using base64 encoding to preserve exact content.""")

        # Encode files
        encoded_files = {}
        for rel_path, analysis in files.items():
            source = analysis.get("source", "")
            if not source:
                continue
            encoded_files[rel_path] = base64.b64encode(source.encode("utf-8")).decode(
                "ascii"
            )

        files_json = json.dumps(encoded_files, indent=2)

        self._code_cell(f"""# Recreate project files
import os, sys, base64

PROJECT_DIR = "/content/{self.project_name}"
os.makedirs(PROJECT_DIR, exist_ok=True)

# All project files (base64-encoded)
encoded_files = {files_json}

created = 0
errors = 0

for rel_path, b64_content in encoded_files.items():
    try:
        full_path = os.path.join(PROJECT_DIR, rel_path)
        parent = os.path.dirname(full_path)
        if parent:
            os.makedirs(parent, exist_ok=True)

        content = base64.b64decode(b64_content).decode("utf-8")
        with open(full_path, "w", encoding="utf-8") as fh:
            fh.write(content)
        created += 1
        print(f"  ✅ {{rel_path}}")
    except Exception as e:
        errors += 1
        print(f"  ❌ {{rel_path}}: {{e}}")

# Add to path
if PROJECT_DIR not in sys.path:
    sys.path.insert(0, PROJECT_DIR)
os.chdir(PROJECT_DIR)

print(f"\\n🎉 Created {{created}} files" + (f" ({{errors}} errors)" if errors else ""))
""")

    def _add_source_code_cells(self):
        """Add source code for each file."""
        files = self.data.get("files", {})
        exec_order = self.data.get("execution_order", [])

        self._md_cell("""## 📝 Source Code

Each file is shown below with its complete source code.""")

        for rel_path in exec_order:
            analysis = files.get(rel_path, {})
            source = analysis.get("source", "")
            if not source:
                continue

            functions = analysis.get("functions", [])
            classes = analysis.get("classes", [])
            line_count = analysis.get("line_count", 0)

            # Markdown header
            md = f"""### 📄 `{rel_path}`

**{line_count} lines** | **{len(functions)} functions** | **{len(classes)} classes**
"""

            if functions:
                md += "\n**Functions:**\n"
                for func in functions[:15]:
                    async_str = "async " if func.get("is_async") else ""
                    md += f"- `{async_str}{func['name']}()`\n"

            if classes:
                md += "\n**Classes:**\n"
                for cls in classes[:10]:
                    md += f"- `{cls['name']}`\n"

            self._md_cell(md)

            # Code cell with full source
            self._code_cell(f"""# ═══════════════════════════════════════════════════════════
# 📄 {rel_path}
# ═══════════════════════════════════════════════════════════

{source}
""")

    def _add_entry_point_cells(self):
        """Execute entry points."""
        entry_points = self.data.get("entry_points", [])
        files = self.data.get("files", {})

        if not entry_points:
            return

        self._md_cell("""## 🎯 Execute Entry Points

Running main entry points with full output capture.""")

        for ep in entry_points:
            analysis = files.get(ep, {})
            has_main_guard = analysis.get("has_main_guard", False)

            self._md_cell(f"""### 🎯 Running: `{ep}`

{"Executing with `__name__ = '__main__'`" if has_main_guard else "Executing as main entry point"}""")

            safe_ep = ep.replace("\\", "\\\\")
            self._code_cell(f"""# Execute {ep}
import os, sys, io, contextlib

PROJECT_DIR = "/content/{self.project_name}"
os.chdir(PROJECT_DIR)
if PROJECT_DIR not in sys.path:
    sys.path.insert(0, PROJECT_DIR)

print("=" * 60)
print(f"  🎯 EXECUTING: {safe_ep}")
print("=" * 60)
print()

ep_filepath = os.path.join(PROJECT_DIR, "{safe_ep}")
if os.path.exists(ep_filepath):
    with open(ep_filepath, "r", encoding="utf-8") as fh:
        ep_source = fh.read()

    output_buf = io.StringIO()
    try:
        ep_namespace = {{"__name__": "__main__", "__file__": ep_filepath}}
        with contextlib.redirect_stdout(output_buf), contextlib.redirect_stderr(output_buf):
            exec(compile(ep_source, "{safe_ep}", "exec"), ep_namespace)
    except SystemExit as exit_err:
        print(f"(Exit code: {{exit_err.code}})")
    except Exception as exc:
        print(output_buf.getvalue())
        print(f"\\n❌ {{type(exc).__name__}}: {{exc}}")
        import traceback; traceback.print_exc()
    else:
        captured = output_buf.getvalue()
        if captured:
            print(captured)

print()
print("=" * 60)
print(f"  ✅ Done: {safe_ep}")
print("=" * 60)
""")

    def _add_summary_cell(self):
        """Add summary."""
        files = self.data.get("files", {})
        total_lines = sum(f.get("line_count", 0) for f in files.values())

        self._md_cell(f"""## ✅ Complete

---

### 📊 Summary
- **Project:** {self.project_name}
- **Files:** {len(files)}
- **Lines of Code:** {total_lines:,}
- **Generated:** {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

---

> All files shown, all entry points executed. 🎉
""")

        self._code_cell("""# Final status
import os

print("✅ ALL CELLS EXECUTED")
print("=" * 50)
print("\\n🎉 Project execution complete!")
print("   All files shown, all entry points executed.")
""")


def main():
    """Main CLI."""
    parser = argparse.ArgumentParser(
        description="🚀 Notebook Generator v3.0 — Minimal & Focused",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=textwrap.dedent("""
        Examples:
          python notebook_generator.py
          python notebook_generator.py --project-dir /path/to/project
          python notebook_generator.py --output notebook.ipynb --exclude tests
          python notebook_generator.py --html  # Also generate HTML report
          python notebook_generator.py --html-only  # Only generate HTML
        """),
    )
    parser.add_argument(
        "--project-dir", "-d", default=".", help="Project directory (default: .)"
    )
    parser.add_argument("--output", "-o", default=None, help="Output notebook filename")
    parser.add_argument(
        "--html-output", default=None, help="Output HTML report filename"
    )
    parser.add_argument(
        "--exclude", "-e", default="", help="Comma-separated exclude patterns"
    )
    parser.add_argument("--html", action="store_true", help="Also generate HTML report")
    parser.add_argument(
        "--html-only",
        action="store_true",
        help="Only generate HTML report (skip notebook)",
    )

    args = parser.parse_args()

    project_dir = os.path.abspath(args.project_dir)
    if not os.path.isdir(project_dir):
        print(f"❌ Error: '{project_dir}' is not a valid directory")
        sys.exit(1)

    exclude = [e.strip() for e in args.exclude.split(",") if e.strip()]
    project_name = Path(project_dir).resolve().name
    output_path = args.output or f"{project_name}_notebook.ipynb"
    if not output_path.endswith(".ipynb"):
        output_path += ".ipynb"
    if not os.path.isabs(output_path):
        output_path = os.path.join(project_dir, output_path)

    html_output = args.html_output or f"{project_name}_report.html"
    if not os.path.isabs(html_output):
        html_output = os.path.join(project_dir, html_output)

    scanner = ProjectScanner(project_dir, exclude_patterns=exclude)
    project_data = scanner.scan()

    # Generate notebook (unless --html-only)
    if not args.html_only:
        generator = NotebookGenerator(project_data)
        generator.generate(output_path)

    # Generate HTML report
    if args.html or args.html_only:
        try:
            from html_visualizer import HTMLVisualizer

            viz = HTMLVisualizer(project_data)
            viz.generate(html_output)
        except ImportError:
            print("  ⚠️  html_visualizer.py not found!")
            print("      Make sure it's in the same directory.")


if __name__ == "__main__":
    main()
