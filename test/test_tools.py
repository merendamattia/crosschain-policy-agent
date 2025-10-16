from pathlib import Path

from src.tools import list_sol_files, read_sol_file


def test_list_and_read(tmp_path):
    # create sample files
    base = tmp_path / "sample"
    base.mkdir()
    f1 = base / "A.sol"
    f1.write_text("pragma solidity ^0.8.0; contract A {}")
    f2 = base / "sub" / "B.sol"
    f2.parent.mkdir()
    f2.write_text("pragma solidity ^0.8.0; contract B {}")

    files = list_sol_files(str(base))
    assert "A.sol" in files or "sample/A.sol" in files

    content = read_sol_file(str(base), "A.sol")
    assert "contract A" in content
