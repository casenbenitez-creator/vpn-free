from __future__ import annotations

import subprocess
from typing import Optional


class ProcessResult:
    def __init__(self, returncode: int, stdout: str, stderr: str) -> None:
        self.returncode = returncode
        self.stdout = stdout
        self.stderr = stderr


def run_sync(
    cmd: list[str],
    timeout: int = 30,
    cwd: Optional[str] = None,
) -> ProcessResult:
    try:
        proc = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd=cwd,
        )
        return ProcessResult(
            returncode=proc.returncode,
            stdout=proc.stdout,
            stderr=proc.stderr,
        )
    except subprocess.TimeoutExpired:
        return ProcessResult(returncode=-1, stdout="", stderr="timeout")
    except FileNotFoundError:
        return ProcessResult(returncode=-2, stdout="", stderr="command not found")
