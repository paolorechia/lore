import os
from pathlib import Path
from dataclasses import dataclass
from typing import Iterable, Tuple

@dataclass
class InMemoryFile:
    path: str
    contents: None


class FileSearcher:
    def __init__(self, base_path: str, *, suffixes: list | None = None):
        self._base_path = Path(base_path)
        self._suffixes: list | None = suffixes or []
        self._files: dict[str, InMemoryFile] = {}


    def get_files(self):
        return self._files

    def find_files(self):
        """Find the files in given path filtered by suffixes."""
        for root, dirs, files in self.walk_with_suffixes(self._base_path):
            for f in files:
                path = os.path.join(root, f)
                with open(path, "r") as fp:
                    contents = fp.read()

                self._files[path] = InMemoryFile(
                    path=path,
                    contents=contents
                )


    def walk_with_suffixes(self, path) -> Iterable[Tuple[str, str, str]]:
        """Walk but applying the suffix filter as an iterator."""
        for root, dirs, files in os.walk(path):
            if not self._suffixes:
                yield root, dirs, files

            filtered_files = []
            for f in files:
                for suffix in self._suffixes:
                    if f.endswith(suffix):
                        filtered_files.append(f)

            yield root, dirs, filtered_files
        