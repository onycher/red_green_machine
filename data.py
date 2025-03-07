from dataclasses import dataclass
from enum import Enum
from pathlib import Path


@dataclass
class Repo:  # noqa: D101
    path: Path
    includes: list[str]
    excludes: list[str]
    test_cmd: str


@dataclass
class File:  # noqa: D101
    path: Path
    content: str


@dataclass
class RepoContent:  # noqa: D101
    files: list[File]


@dataclass
class EndStatus:  # noqa: D101
    tests_passed: bool = False
    implemented_file: bool = False
    failed: bool = True


class Stage(str, Enum):  # noqa: D101
    init = "init"
    implement = "implement"
    refactor = "refactor"
