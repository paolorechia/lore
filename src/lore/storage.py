"""Local storage primitives. Source repositories are never executed."""
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import subprocess
import tempfile


class LoreError(ValueError):
    """An actionable input or repository error."""


def encode(value):
    return json.dumps(value, ensure_ascii=True, sort_keys=True, indent=2) + "\n"


def digest(data):
    return hashlib.sha256(data).hexdigest()


def safe_path(root, relative):
    if not isinstance(relative, str) or not relative or "\\" in relative:
        raise LoreError("Expected a repository-relative POSIX path")
    parts = PurePosixPath(relative)
    if parts.is_absolute() or ".." in parts.parts:
        raise LoreError("Path must stay inside the repository")
    current = root
    for part in parts.parts:
        current = current / part
        if current.is_symlink():
            raise LoreError(f"Symlink paths are not supported: {relative}")
    if not current.resolve().is_relative_to(root):
        raise LoreError("Path escapes repository")
    return current


def git(root, *args, input=None, allowed=(0,)):
    result = subprocess.run(["git", "-C", str(root), *args], input=input, capture_output=True)
    if result.returncode not in allowed:
        raise LoreError("Git operation failed; use an accessible Git repository")
    return result.stdout


def repository(path):
    root = Path(path).expanduser().resolve(strict=True)
    if not root.is_dir():
        raise LoreError("Repository path must be a directory")
    top = Path(os.fsdecode(git(root, "rev-parse", "--show-toplevel")).strip()).resolve()
    if root != top:
        raise LoreError(f"Use repository root {top}; narrow evidence with --include")
    return root


def read_json(path):
    if path.stat().st_size > 16_000_000:
        raise LoreError("JSON input exceeds 16 MB limit")
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (ValueError, UnicodeError) as error:
        raise LoreError(f"Invalid JSON in {path.name}") from error


def write_once(path, text):
    """Publish complete bytes without replacing an existing artifact."""
    data = text.encode("utf-8")
    if path.is_symlink():
        raise LoreError("Refusing to write through symlink")
    if path.exists():
        if path.read_bytes() != data:
            raise LoreError(f"Existing artifact differs: {path}. Prepare a new run or use another result.")
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, name = tempfile.mkstemp(dir=path.parent)
    try:
        with os.fdopen(fd, "wb") as stream:
            stream.write(data)
        try:
            os.link(name, path)
        except FileExistsError:
            if path.is_symlink() or path.read_bytes() != data:
                raise LoreError(f"Conflicting artifact: {path}")
    finally:
        os.unlink(name)


def initialize(root):
    for folder in (".lore", ".lore/knowledge", ".lore/runs", ".lore/candidates"):
        safe_path(root, folder).mkdir(parents=True, exist_ok=True)
    ignore = safe_path(root, ".lore/.gitignore")
    # Preserve user rules while ensuring generated artifacts stay local.
    existing = ignore.read_text() if ignore.exists() else ""
    missing = [rule for rule in ("/runs/", "/candidates/") if rule not in existing.splitlines()]
    if missing:
        with ignore.open("a", encoding="utf-8") as stream:
            stream.write(("\n" if existing and not existing.endswith("\n") else "") + "\n".join(missing) + "\n")
    return root / ".lore"
