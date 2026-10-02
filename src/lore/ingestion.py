"""Deterministic, bounded source evidence; no inference or persistence."""
import ast
from fnmatch import fnmatchcase
import os
from pathlib import PurePosixPath

from .storage import LoreError, digest, git, safe_path

SUFFIXES = {".py", ".ts", ".tsx", ".js", ".jsx", ".mjs", ".cjs", ".go", ".rs",
            ".java", ".kt", ".swift", ".rb", ".php", ".cs", ".c", ".h", ".cpp",
            ".hpp", ".sh", ".sql", ".vue", ".svelte"}
EXCLUDED = {".git", ".lore", "node_modules", "vendor", ".venv", "venv", "dist", "build", "__pycache__"}


def matches(path, pattern):
    # **/ can match zero directories, unlike fnmatch's literal slash behavior.
    if fnmatchcase(path, pattern):
        return True
    if "**/" in pattern:
        return matches(path, pattern.replace("**/", "", 1))
    return False


def collect(root, *, includes=(), include_untracked=False, max_files=40,
            max_file_bytes=24000, max_bytes=120000):
    if any(type(v) is not int or v <= 0 for v in (max_files, max_file_bytes, max_bytes)):
        raise LoreError("Evidence limits must be positive integers")
    args = ["ls-files", "--cached", "--exclude-standard", "-z"]
    if include_untracked:
        args.append("--others")
    paths = sorted(set(os.fsdecode(p) for p in git(root, *args).split(b"\0") if p))
    ignored = set()
    if paths:
        raw = git(root, "check-ignore", "--no-index", "--stdin", "-z",
                  input=b"\0".join(os.fsencode(p) for p in paths) + b"\0", allowed=(0, 1))
        ignored = {os.fsdecode(p) for p in raw.split(b"\0") if p}
    evidence, skipped, warnings = [], [], []
    count = total = 0
    for name in paths:
        posix = PurePosixPath(name)
        if posix.suffix not in SUFFIXES or (includes and not any(matches(name, p) for p in includes)):
            continue
        reason = None
        if name in ignored or EXCLUDED.intersection(posix.parts):
            reason = "ignored or generated directory"
        elif count >= max_files:
            reason = "file count budget"
        if reason:
            skipped.append({"path": name, "reason": reason})
            continue
        try:
            path = safe_path(root, name)
            if not path.is_file():
                raise LoreError("not a regular file")
            if path.stat().st_size > max_file_bytes:
                raise LoreError("file byte budget")
            raw = path.read_bytes()
            if len(raw) > max_file_bytes:
                raise LoreError("file byte budget")
            if total + len(raw) > max_bytes:
                raise LoreError("total byte budget")
            content = raw.decode("utf-8")
            if "\x00" in content or not content.strip():
                raise LoreError("binary or empty file")
        except (OSError, UnicodeError, LoreError) as error:
            skipped.append({"path": name, "reason": str(error)})
            continue
        count += 1
        total += len(raw)
        sha = digest(raw)
        lines = content.splitlines()
        evidence.append({"id": f"E-{len(evidence)+1:04d}", "path": name, "sha256": sha,
                         "start_line": 1, "end_line": len(lines), "type": "source", "text": content})
        if posix.suffix == ".py":
            try:
                tree = ast.parse(content)
                nodes = sorted((n for n in ast.walk(tree) if isinstance(n, (ast.Import, ast.ImportFrom))),
                               key=lambda n: n.lineno)
                for node in nodes:
                    evidence.append({"id": f"E-{len(evidence)+1:04d}", "path": name,
                                     "sha256": sha, "start_line": node.lineno,
                                     "end_line": node.end_lineno, "type": "python_import",
                                     "text": "\n".join(lines[node.lineno-1:node.end_lineno])})
            except (SyntaxError, ValueError, RecursionError) as error:
                warnings.append({"path": name, "reason": f"Python AST unavailable: {type(error).__name__}"})
    if not evidence:
        raise LoreError("No source evidence selected. Check --include, budgets, or use --include-untracked for new files.")
    return {"evidence": evidence, "coverage": {"included_files": count, "source_bytes": total,
            "skipped": skipped, "warnings": warnings,
            "limitations": "Bounded selected working-tree source only; Python AST imports, raw source for other languages. No runtime or intent proof."}}
