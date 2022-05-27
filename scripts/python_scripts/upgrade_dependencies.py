"""Upgrade the package's current dependencies.

NOTE: This upgrades the dependencies outside their specified boundaries.
"""
import subprocess
from collections.abc import MutableMapping
from functools import reduce
from pathlib import Path
from typing import Any, Optional, Union

import toml


def _toml_file(path: Optional[Path] = None) -> MutableMapping[str, Any]:
    if path is None:
        path = Path.cwd()
    path_glob = path.glob("pyproject.toml")
    current_toml = next(path_glob, None)
    if current_toml is None:
        raise FileNotFoundError(f"pyproject.toml was not found in {path}")
    return toml.load(current_toml)


def _reduce_packages(state: list[str], item: tuple[str, Union[str, dict[str, Any]]]) -> list[str]:
    name, details = item
    if isinstance(details, str):
        return state + [f"{name}@latest"]

    if isinstance(details, dict):
        if extras := details.get("extras"):
            extras_str = ",".join(extras)
            return state + [f"{name}[{extras_str}]@latest"]

    print(f"warn: skipping {name} as it has unsupported details {details}.")
    return state


def _poetry_add_latest(packages: MutableMapping[str, Any], dev: bool = False) -> None:
    if dev:
        initial_command = ["poetry", "add", "--dev"]
    else:
        initial_command = ["poetry", "add"]

    package_item_iter = packages.items()
    final_command = reduce(_reduce_packages, package_item_iter, initial_command)
    subprocess.run(final_command)


def main() -> None:
    """Upgrade the poetry-managed project's dependencies.

    Raises
    ------
    FileNotFoundError
        Whenever no pyproject.toml is found recursively in `cwd`.
    """
    pyproject_toml = _toml_file()
    tool_poetry = pyproject_toml["tool"]["poetry"]
    dependencies: MutableMapping[str, Any] = tool_poetry["dependencies"]
    dependencies.pop("python", None)
    _poetry_add_latest(dependencies)
    dev_dependencies = tool_poetry["dev-dependencies"]
    _poetry_add_latest(dev_dependencies, dev=True)


if __name__ == "__main__":
    main()
