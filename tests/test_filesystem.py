import pytest
import tempfile
import os
from lore.file_system import FileSearcher
from copy import copy

@pytest.fixture
def file1():
    return """
import math

math.floor(2.4) + math.floor(3.8)
"""

@pytest.fixture
def file2():
    return """
import pytest

def test_example():
    assert 2 + 2
"""


@pytest.fixture
def file3():
    return """

import invalid_library
print("wow, much goodz")
"""


@pytest.fixture
def test_files(file1, file2, file3):
    return {
        "dir1/file1.py": file1,
        "dir1/file2.py": file2,
        "dir2/subdir1/file3.py": file3
    }


@pytest.fixture
def dir_list():
    return ["dir1", "dir2", "dir3", "dir2/subdir1"]


@pytest.fixture
def tmp_file_system(dir_list, test_files):
    with tempfile.TemporaryDirectory() as tmp_dir:
        for d in dir_list:
            created_dir = os.path.join(tmp_dir, d)
            os.makedirs(created_dir)

        for path, content in test_files.items():
            tmp_path = os.path.join(tmp_dir, path)
            print(f"Creating test file {tmp_path}")
            with open(tmp_path, "w") as fp:
                fp.write(content)

        yield tmp_dir            


def test_file_searcher(tmp_file_system, test_files):
    file_searcher = FileSearcher(tmp_file_system)
    file_searcher.find_files()
    read_files = file_searcher.get_files()

    assert len(read_files) == 3

    found_files = copy(test_files)

    for path_suffix, _ in test_files.items():
        for read_path, in_memory_file in read_files.items():
            if read_path.endswith(path_suffix):
                found_files[path_suffix] = in_memory_file

    assert len(found_files) == 3
    for key, expected_content in test_files.items():
        assert found_files[key].contents == expected_content
