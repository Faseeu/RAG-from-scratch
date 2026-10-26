#!/usr/bin/env python3
"""
Via Negativa Approved Features
Only features that pass the test: "Would removing this make the tool worse?"

1. Docstring + Type Coverage (fundamental maintainability metric)
2. Exception Handling Analysis (real bugs: bare except, swallowed errors)
3. Resource Leak Detection (real bugs: unclosed files/connections)
4. Code Duplication Detection (DRY violations)
5. Git History Analysis (temporal dimension, hot spots)
6. Environment Variable Detection (deployment-critical)
7. Refactoring Suggestions (actionable advice)
"""

import ast
import os
import re
import subprocess
from collections import defaultdict, Counter
from typing import Dict, List, Any, Optional, Set
from pathlib import Path


# ═════════════════════════════════════════════════════════════════════════════
# 1. DOCSTRING + TYPE COVERAGE ANALYZER
# ═════════════════════════════════════════════════════════════════════════════

class DocumentationAnalyzer:
    """Analyze docstring and type hint coverage."""

    @staticmethod
    def analyze(files: Dict[str, Dict]) -> Dict[str, Any]:
        total_functions = 0
        functions_with_docstring = 0
        functions_with_type_hints = 0
        functions_with_both = 0
        total_classes = 0
        classes_with_docstring = 0

        undocumented_functions = []
        untyped_functions = []

        for rel_path, analysis in files.items():
            for func in analysis.get("functions", []):
                total_functions += 1
                has_doc = bool(func.get("docstring"))
                has_types = bool(func.get("return_type") or
                                any(a != "self" and ":" in str(a)
                                    for a in func.get("args", [])))

                # Check args for type hints in source
                source = analysis.get("source", "")
                if source:
                    lines = source.splitlines()
                    func_line = func.get("line", 0) - 1
                    if 0 <= func_line < len(lines):
                        def_line = lines[func_line]
                        has_types = has_types or (":" in def_line and "->" in def_line)

                if has_doc:
                    functions_with_docstring += 1
                else:
                    undocumented_functions.append({
                        "file": rel_path,
                        "function": func["name"],
                        "line": func.get("line", 0),
                        "class": func.get("class"),
                    })

                if has_types:
                    functions_with_type_hints += 1
                else:
                    untyped_functions.append({
                        "file": rel_path,
                        "function": func["name"],
                        "line": func.get("line", 0),
                    })

                if has_doc and has_types:
                    functions_with_both += 1

            for cls in analysis.get("classes", []):
                total_classes += 1
                if cls.get("docstring"):
                    classes_with_docstring += 1

        doc_coverage = (functions_with_docstring / max(total_functions, 1)) * 100
        type_coverage = (functions_with_type_hints / max(total_functions, 1)) * 100
        full_coverage = (functions_with_both / max(total_functions, 1)) * 100
        class_doc_coverage = (classes_with_docstring / max(total_classes, 1)) * 100

        return {
            "total_functions": total_functions,
            "functions_with_docstring": functions_with_docstring,
            "functions_with_type_hints": functions_with_type_hints,
            "functions_with_both": functions_with_both,
            "docstring_coverage": round(doc_coverage, 1),
            "type_hint_coverage": round(type_coverage, 1),
            "full_coverage": round(full_coverage, 1),
            "total_classes": total_classes,
            "classes_with_docstring": classes_with_docstring,
            "class_doc_coverage": round(class_doc_coverage, 1),
            "undocumented_functions": undocumented_functions[:20],
            "untyped_functions": untyped_functions[:20],
        }


# ═════════════════════════════════════════════════════════════════════════════
# 2. EXCEPTION HANDLING ANALYZER
# ═════════════════════════════════════════════════════════════════════════════

class ExceptionAnalyzer:
    """Detect exception handling anti-patterns."""

    @staticmethod
    def analyze_file(filepath: str, source: str) -> List[Dict[str, Any]]:
        issues = []
        try:
            tree = ast.parse(source, filename=filepath)
        except SyntaxError:
            return issues

        for node in ast.walk(tree):
            if isinstance(node, ast.ExceptHandler):
                line = node.lineno

                # 1. Bare except (catches everything)
                if node.type is None:
                    issues.append({
                        "type": "bare_except",
                        "severity": "HIGH",
                        "line": line,
                        "message": "Bare 'except:' catches ALL exceptions including KeyboardInterrupt and SystemExit",
                        "suggestion": "Use 'except Exception:' instead, or catch specific exceptions",
                    })

                # 2. except: pass (swallowed error)
                if node.type is None and len(node.body) == 1:
                    body = node.body[0]
                    if isinstance(body, ast.Pass):
                        issues.append({
                            "type": "swallowed_exception",
                            "severity": "HIGH",
                            "line": line,
                            "message": "Bare 'except: pass' silently swallows ALL errors",
                            "suggestion": "At minimum log the error, or catch specific exceptions",
                        })
                    elif (isinstance(body, ast.Expr) and
                          isinstance(body.value, ast.Constant) and
                          isinstance(body.value.value, str)):
                        issues.append({
                            "type": "swallowed_exception",
                            "severity": "MEDIUM",
                            "line": line,
                            "message": "Bare except with only a docstring — error is silently swallowed",
                            "suggestion": "Handle or log the exception",
                        })

                # 3. except Exception: pass (too broad + swallowed)
                if (isinstance(node.type, ast.Name) and
                    node.type.id == "Exception" and
                    len(node.body) == 1 and
                    isinstance(node.body[0], ast.Pass)):
                    issues.append({
                        "type": "broad_except_pass",
                        "severity": "MEDIUM",
                        "line": line,
                        "message": "'except Exception: pass' swallows all standard errors",
                        "suggestion": "Catch specific exceptions or log the error",
                    })

                # 4. except Exception as e (but e is never used)
                if (isinstance(node.type, ast.Name) and
                    node.type.id == "Exception" and
                    node.name):
                    # Check if the exception variable is used in the body
                    used = False
                    for child in ast.walk(ast.Module(body=node.body, type_ignores=[])):
                        if isinstance(child, ast.Name) and child.id == node.name:
                            used = True
                            break
                    if not used:
                        issues.append({
                            "type": "unused_exception_var",
                            "severity": "LOW",
                            "line": line,
                            "message": f"Exception variable '{node.name}' is caught but never used",
                            "suggestion": f"Remove 'as {node.name}' or use it for logging",
                        })

        # 5. Detect try blocks with too many statements (should be narrow)
        for node in ast.walk(tree):
            if isinstance(node, ast.Try):
                try_lines = sum(
                    getattr(stmt, 'end_lineno', stmt.lineno) - stmt.lineno + 1
                    for stmt in node.body
                )
                if try_lines > 30:
                    issues.append({
                        "type": "broad_try_block",
                        "severity": "MEDIUM",
                        "line": node.lineno,
                        "message": f"Try block covers {try_lines} lines — too broad",
                        "suggestion": "Narrow the try block to only the code that might raise",
                    })

        return issues


# ═════════════════════════════════════════════════════════════════════════════
# 3. RESOURCE LEAK DETECTOR
# ═════════════════════════════════════════════════════════════════════════════

class ResourceLeakDetector:
    """Detect potential resource leaks (unclosed files, connections)."""

    @staticmethod
    def analyze_file(filepath: str, source: str) -> List[Dict[str, Any]]:
        issues = []
        try:
            tree = ast.parse(source, filename=filepath)
        except SyntaxError:
            return issues

        # Track open() calls and whether they're in a with statement
        with_resources = set()  # line numbers of open() inside with

        # Find all with statements and their resource expressions
        for node in ast.walk(tree):
            if isinstance(node, ast.With):
                for item in node.items:
                    # Mark all Call nodes inside the with items
                    for child in ast.walk(item.context_expr):
                        if isinstance(child, ast.Call):
                            with_resources.add(child.lineno)

        # Find all open() calls NOT inside a with statement
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                call_name = None
                if isinstance(node.func, ast.Name):
                    call_name = node.func.id
                elif isinstance(node.func, ast.Attribute):
                    if isinstance(node.func.value, ast.Name):
                        call_name = f"{node.func.value.id}.{node.func.attr}"

                # open() without with
                if call_name == "open" and node.lineno not in with_resources:
                    # Check if the result is assigned to a variable
                    # (might be closed later — we can't be sure, so flag it)
                    issues.append({
                        "type": "unclosed_file",
                        "severity": "MEDIUM",
                        "line": node.lineno,
                        "message": "open() called without 'with' statement — file may not be closed",
                        "suggestion": "Use 'with open(...) as f:' to ensure the file is closed",
                    })

                # Database connections without context manager
                db_connect_patterns = [
                    "connect", "connection", "create_engine",
                    "sqlite3.connect", "psycopg2.connect",
                    "pymongo.MongoClient", "redis.Redis",
                ]
                if call_name and any(p in call_name for p in db_connect_patterns):
                    if node.lineno not in with_resources:
                        issues.append({
                            "type": "unclosed_connection",
                            "severity": "HIGH",
                            "line": node.lineno,
                            "message": f"Database connection '{call_name}' without context manager",
                            "suggestion": "Use 'with' statement or ensure .close() is called",
                        })

                # requests.get without timeout
                if call_name in ("requests.get", "requests.post",
                                  "requests.put", "requests.delete",
                                  "requests.patch", "requests.head"):
                    has_timeout = any(kw.arg == "timeout" for kw in node.keywords)
                    if not has_timeout:
                        issues.append({
                            "type": "missing_timeout",
                            "severity": "MEDIUM",
                            "line": node.lineno,
                            "message": f"{call_name}() called without timeout — may hang indefinitely",
                            "suggestion": f"Add timeout parameter: {call_name}(..., timeout=30)",
                        })

        return issues


# ═════════════════════════════════════════════════════════════════════════════
# 4. CODE DUPLICATION DETECTOR
# ═════════════════════════════════════════════════════════════════════════════

class DuplicationDetector:
    """Detect code duplication across project files."""

    MIN_LINES = 6  # Minimum lines to consider as duplication

    @classmethod
    def analyze(cls, files: Dict[str, Dict]) -> Dict[str, Any]:
        # Extract normalized line sequences from each file
        file_lines = {}
        for rel_path, analysis in files.items():
            source = analysis.get("source", "")
            if not source:
                continue
            lines = source.splitlines()
            # Normalize: strip whitespace, skip empty/comment lines
            normalized = []
            for i, line in enumerate(lines):
                stripped = line.strip()
                if stripped and not stripped.startswith("#"):
                    normalized.append((i + 1, stripped))
            file_lines[rel_path] = normalized

        # Find duplicate blocks using a sliding window approach
        duplicates = []
        seen_pairs = set()

        file_list = list(file_lines.items())
        for i, (path_a, lines_a) in enumerate(file_list):
            for j, (path_b, lines_b) in enumerate(file_list):
                if i >= j:
                    continue

                # Find matching sequences
                matches = cls._find_matching_blocks(
                    lines_a, lines_b, path_a, path_b
                )
                for match in matches:
                    pair_key = tuple(sorted([
                        f"{match['file_a']}:{match['line_a']}",
                        f"{match['file_b']}:{match['line_b']}",
                    ]))
                    if pair_key not in seen_pairs:
                        seen_pairs.add(pair_key)
                        duplicates.append(match)

        # Also find within-file duplication
        for path, lines in file_lines.items():
            matches = cls._find_within_file_duplicates(lines, path)
            duplicates.extend(matches)

        # Sort by block size (largest first)
        duplicates.sort(key=lambda d: -d.get("lines", 0))

        # Calculate total duplicated lines
        total_dup_lines = sum(d.get("lines", 0) for d in duplicates)
        total_lines = sum(len(lines) for lines in file_lines.values())
        dup_percentage = (total_dup_lines / max(total_lines, 1)) * 100

        return {
            "duplicates": duplicates[:30],  # Top 30
            "total_duplicate_blocks": len(duplicates),
            "total_duplicate_lines": total_dup_lines,
            "total_lines": total_lines,
            "duplication_percentage": round(dup_percentage, 1),
        }

    @classmethod
    def _find_matching_blocks(cls, lines_a, lines_b, path_a, path_b):
        """Find matching code blocks between two files."""
        matches = []
        min_lines = cls.MIN_LINES

        i = 0
        while i < len(lines_a):
            best_match = 0
            best_j = -1

            for j in range(len(lines_b)):
                match_len = 0
                while (i + match_len < len(lines_a) and
                       j + match_len < len(lines_b) and
                       lines_a[i + match_len][1] == lines_b[j + match_len][1]):
                    match_len += 1

                if match_len >= min_lines and match_len > best_match:
                    best_match = match_len
                    best_j = j

            if best_match >= min_lines:
                matches.append({
                    "file_a": path_a,
                    "line_a": lines_a[i][0],
                    "file_b": path_b,
                    "line_b": lines_b[best_j][0],
                    "lines": best_match,
                    "type": "cross_file",
                    "preview": lines_a[i][1][:80],
                })
                i += best_match
            else:
                i += 1

        return matches

    @classmethod
    def _find_within_file_duplicates(cls, lines, path):
        """Find duplicate blocks within the same file."""
        matches = []
        min_lines = cls.MIN_LINES
        seen = set()

        for i in range(len(lines)):
            for j in range(i + min_lines, len(lines)):
                if (i, j) in seen:
                    continue

                match_len = 0
                while (i + match_len < len(lines) and
                       j + match_len < len(lines) and
                       i + match_len < j and
                       lines[i + match_len][1] == lines[j + match_len][1]):
                    match_len += 1

                if match_len >= min_lines:
                    for k in range(match_len):
                        seen.add((i + k, j + k))
                    matches.append({
                        "file_a": path,
                        "line_a": lines[i][0],
                        "file_b": path,
                        "line_b": lines[j][0],
                        "lines": match_len,
                        "type": "within_file",
                        "preview": lines[i][1][:80],
                    })

        return matches


# ═════════════════════════════════════════════════════════════════════════════
# 5. GIT HISTORY ANALYZER
# ═════════════════════════════════════════════════════════════════════════════

class GitHistoryAnalyzer:
    """Analyze git history for churn rate, hot spots, and contributor info."""

    @staticmethod
    def analyze(project_dir: str, files: Dict[str, Dict]) -> Optional[Dict[str, Any]]:
        """Analyze git history. Returns None if not a git repo."""
        git_dir = Path(project_dir) / ".git"
        if not git_dir.exists():
            return None

        try:
            # Get commit count per file
            result = subprocess.run(
                ["git", "log", "--format=format:", "--name-only", "--pretty=format:"],
                capture_output=True, text=True, cwd=project_dir, timeout=30
            )
            file_commits = Counter()
            for line in result.stdout.strip().splitlines():
                line = line.strip()
                if line:
                    file_commits[line] += 1

            # Get last modified date per file
            result2 = subprocess.run(
                ["git", "log", "-1", "--format=%ai", "--name-only"],
                capture_output=True, text=True, cwd=project_dir, timeout=30
            )

            # Get contributor count
            result3 = subprocess.run(
                ["git", "shortlog", "-sn", "--all"],
                capture_output=True, text=True, cwd=project_dir, timeout=30
            )
            contributors = []
            for line in result3.stdout.strip().splitlines():
                parts = line.strip().split("\t", 1)
                if len(parts) == 2:
                    contributors.append({
                        "commits": int(parts[0].strip()),
                        "name": parts[1].strip(),
                    })

            # Get total commit count
            result4 = subprocess.run(
                ["git", "rev-list", "--count", "HEAD"],
                capture_output=True, text=True, cwd=project_dir, timeout=30
            )
            total_commits = int(result4.stdout.strip()) if result4.stdout.strip() else 0

            # Build churn data for project files
            churn_data = []
            for rel_path in files:
                commits = file_commits.get(rel_path, 0)
                complexity = files[rel_path].get("complexity_score", 0)
                mi = files[rel_path].get("maintainability_index", 50)
                # Hot spot score: high churn + high complexity
                hot_spot_score = commits * complexity / 100

                churn_data.append({
                    "file": rel_path,
                    "commits": commits,
                    "complexity": complexity,
                    "hot_spot_score": round(hot_spot_score, 2),
                })

            # Sort by hot spot score
            churn_data.sort(key=lambda x: -x["hot_spot_score"])

            # Find hot spots (high churn + high complexity)
            hot_spots = [
                d for d in churn_data
                if d["commits"] > 5 and d["complexity"] > 10
            ][:10]

            return {
                "available": True,
                "total_commits": total_commits,
                "contributors": contributors[:10],
                "contributor_count": len(contributors),
                "file_churn": churn_data[:20],
                "hot_spots": hot_spots,
                "most_changed": [
                    {"file": f, "commits": c}
                    for f, c in file_commits.most_common(10)
                    if f in files
                ],
            }

        except Exception as e:
            return {"available": False, "error": str(e)}


# ═════════════════════════════════════════════════════════════════════════════
# 6. ENVIRONMENT VARIABLE DETECTOR
# ═════════════════════════════════════════════════════════════════════════════

class EnvVarDetector:
    """Detect all environment variables used in the project."""

    @staticmethod
    def analyze(files: Dict[str, Dict]) -> Dict[str, Any]:
        env_vars = {}

        for rel_path, analysis in files.items():
            source = analysis.get("source", "")
            if not source:
                continue

            # Detect os.environ['VAR'] and os.environ.get('VAR')
            patterns = [
                # os.environ['VAR'] or os.environ["VAR"]
                r"os\.environ\[['\"](\w+)['\"]\]",
                # os.environ.get('VAR') or os.environ.get("VAR")
                r"os\.environ\.get\(['\"](\w+)['\"]",
                # os.getenv('VAR') or os.getenv("VAR")
                r"os\.getenv\(['\"](\w+)['\"]",
                # environ['VAR']
                r"(?<!\w)environ\[['\"](\w+)['\"]\]",
                # environ.get('VAR')
                r"(?<!\w)environ\.get\(['\"](\w+)['\"]",
                # getenv('VAR')
                r"(?<!\w)getenv\(['\"](\w+)['\"]",
            ]

            for pattern in patterns:
                for match in re.finditer(pattern, source):
                    var_name = match.group(1)
                    # Find line number
                    line_num = source[:match.start()].count("\n") + 1

                    # Check if there's a default value
                    context = source[match.start():match.end() + 50]
                    has_default = "get(" in context and "," in context

                    if var_name not in env_vars:
                        env_vars[var_name] = {
                            "name": var_name,
                            "files": [],
                            "has_default": has_default,
                        }
                    env_vars[var_name]["files"].append({
                        "file": rel_path,
                        "line": line_num,
                        "has_default": has_default,
                    })

        # Sort by usage frequency
        sorted_vars = sorted(
            env_vars.values(),
            key=lambda v: -len(v["files"])
        )

        vars_without_defaults = [
            v for v in sorted_vars
            if not any(f["has_default"] for f in v["files"])
        ]

        return {
            "env_vars": sorted_vars,
            "total_unique": len(env_vars),
            "required_vars": vars_without_defaults,
            "total_usage": sum(len(v["files"]) for v in env_vars.values()),
        }


# ═════════════════════════════════════════════════════════════════════════════
# 7. REFACTORING SUGGESTIONS
# ═════════════════════════════════════════════════════════════════════════════

class RefactoringAdvisor:
    """Generate actionable refactoring suggestions from code analysis."""

    @staticmethod
    def generate(files: Dict[str, Dict], code_smells: List[Dict],
                 security_issues: List[Dict], exception_issues: List[Dict],
                 resource_leaks: List[Dict]) -> List[Dict[str, Any]]:
        suggestions = []

        # From code smells
        for smell in code_smells:
            smell_type = smell.get("type", "")
            if smell_type == "long_function":
                suggestions.append({
                    "priority": "HIGH",
                    "category": "Extract Method",
                    "file": smell.get("file", ""),
                    "target": smell.get("name", ""),
                    "suggestion": (
                        f"Extract parts of '{smell.get('name', '')}' into smaller functions. "
                        f"Look for logical blocks that can be named and separated."
                    ),
                    "technique": "Extract Method (Martin Fowler)",
                })
            elif smell_type == "too_many_params":
                suggestions.append({
                    "priority": "MEDIUM",
                    "category": "Introduce Parameter Object",
                    "file": smell.get("file", ""),
                    "target": smell.get("name", ""),
                    "suggestion": (
                        f"Group parameters of '{smell.get('name', '')}' into a config/dataclass object. "
                        f"Consider using @dataclass or TypedDict."
                    ),
                    "technique": "Introduce Parameter Object",
                })
            elif smell_type == "deep_nesting":
                suggestions.append({
                    "priority": "HIGH",
                    "category": "Replace Nested Conditional with Guard Clauses",
                    "file": smell.get("file", ""),
                    "target": smell.get("name", ""),
                    "suggestion": (
                        f"Use early returns (guard clauses) in '{smell.get('name', '')}' "
                        f"to reduce nesting. Return early for error cases."
                    ),
                    "technique": "Replace Nested Conditional with Guard Clauses",
                })
            elif smell_type == "god_class":
                suggestions.append({
                    "priority": "HIGH",
                    "category": "Extract Class",
                    "file": smell.get("file", ""),
                    "target": smell.get("name", ""),
                    "suggestion": (
                        f"Split '{smell.get('name', '')}' into smaller, focused classes. "
                        f"Group related methods together."
                    ),
                    "technique": "Extract Class",
                })

        # From exception issues
        for issue in exception_issues:
            if issue.get("type") == "bare_except":
                suggestions.append({
                    "priority": "HIGH",
                    "category": "Narrow Exception Handling",
                    "file": issue.get("file", ""),
                    "target": f"line {issue.get('line', '?')}",
                    "suggestion": (
                        "Replace bare 'except:' with specific exception types. "
                        "Use 'except (ValueError, TypeError):' for expected errors."
                    ),
                    "technique": "Specific Exception Handling",
                })

        # From resource leaks
        for issue in resource_leaks:
            if issue.get("type") == "unclosed_file":
                suggestions.append({
                    "priority": "MEDIUM",
                    "category": "Use Context Manager",
                    "file": issue.get("file", ""),
                    "target": f"line {issue.get('line', '?')}",
                    "suggestion": (
                        "Replace 'f = open(...)' with 'with open(...) as f:' "
                        "to ensure the file is always closed."
                    ),
                    "technique": "Context Manager (with statement)",
                })
            elif issue.get("type") == "missing_timeout":
                suggestions.append({
                    "priority": "MEDIUM",
                    "category": "Add Timeout",
                    "file": issue.get("file", ""),
                    "target": f"line {issue.get('line', '?')}",
                    "suggestion": (
                        "Add a timeout to prevent indefinite hanging. "
                        "Use timeout=30 or a configurable value."
                    ),
                    "technique": "Defensive Programming",
                })

        # From security issues
        for issue in security_issues:
            if issue.get("type") == "hardcoded_secret":
                suggestions.append({
                    "priority": "CRITICAL",
                    "category": "Externalize Secrets",
                    "file": issue.get("file", ""),
                    "target": issue.get("variable", ""),
                    "suggestion": (
                        f"Move '{issue.get('variable', '')}' to environment variables "
                        f"or a secrets manager. Never commit secrets to version control."
                    ),
                    "technique": "Externalize Configuration",
                })

        # Sort by priority
        priority_order = {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2, "LOW": 3}
        suggestions.sort(key=lambda s: priority_order.get(s.get("priority", "LOW"), 99))

        return suggestions


# ═════════════════════════════════════════════════════════════════════════════
# INTEGRATION: Run all via-negativa analyzers
# ═════════════════════════════════════════════════════════════════════════════

def run_all_analyses(files: Dict[str, Dict], project_dir: str) -> Dict[str, Any]:
    """Run all via-negativa-approved analyses and return combined results."""

    results = {}

    # 1. Documentation coverage
    results["doc_coverage"] = DocumentationAnalyzer.analyze(files)

    # 2. Exception handling
    all_exception_issues = []
    for rel_path, analysis in files.items():
        source = analysis.get("source", "")
        if source:
            issues = ExceptionAnalyzer.analyze_file(rel_path, source)
            for issue in issues:
                issue["file"] = rel_path
            all_exception_issues.extend(issues)
    results["exception_issues"] = all_exception_issues

    # 3. Resource leaks
    all_leak_issues = []
    for rel_path, analysis in files.items():
        source = analysis.get("source", "")
        if source:
            issues = ResourceLeakDetector.analyze_file(rel_path, source)
            for issue in issues:
                issue["file"] = rel_path
            all_leak_issues.extend(issues)
    results["resource_leaks"] = all_leak_issues

    # 4. Code duplication
    results["duplication"] = DuplicationDetector.analyze(files)

    # 5. Git history
    results["git_history"] = GitHistoryAnalyzer.analyze(project_dir, files)

    # 6. Environment variables
    results["env_vars"] = EnvVarDetector.analyze(files)

    # 7. Refactoring suggestions
    results["refactoring_suggestions"] = RefactoringAdvisor.generate(
        files,
        code_smells=[],  # Will be populated by caller
        security_issues=[],  # Will be populated by caller
        exception_issues=all_exception_issues,
        resource_leaks=all_leak_issues,
    )

    return results
