import os
from pathlib import Path
from typing import List

from datapizza.tools import tool


@tool
def list_sol_files(folder: str) -> List[str]:
    """List all Solidity source files under `folder`.

    This function is registered as a Datapizza tool via the `@tool` decorator and is
    intended for use by the agent during planning. It returns relative paths to all
    files ending in `.sol` beneath the provided directory.

    Args:
        folder: Path to the directory to scan for `.sol` files. May be absolute or
            relative to the current working directory.

    Returns:
        A list of relative string paths to `.sol` files. Returns an empty list if the
        folder does not exist or no `.sol` files are found.
    """
    base = Path(folder)
    if not base.exists():
        return []
    files = [str(p.relative_to(base)) for p in base.rglob("*.sol") if p.is_file()]
    return files


@tool
def read_sol_file(folder: str, relative_path: str) -> str:
    """Read the contents of a Solidity file and return it as text.

    This function is registered as a Datapizza tool and is intended to allow the
    agent to retrieve the contents of a specific `.sol` file discovered by
    `list_sol_files`.

    Args:
        folder: Base directory where the file lives (same base used with
            `list_sol_files`).
        relative_path: Relative path (returned by `list_sol_files`) to the file to
            read.

    Returns:
        The file contents as a string. If the file cannot be read an error string
        describing the failure is returned instead (the agent will see this text).
    """
    p = Path(folder) / relative_path
    try:
        return p.read_text()
    except Exception as e:
        return f"<error reading {relative_path}: {e}>"
