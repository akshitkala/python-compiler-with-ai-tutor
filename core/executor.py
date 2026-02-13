import subprocess
import sys
import tempfile
import os

# Default timeout in seconds
EXECUTION_TIMEOUT = 5


def execute_safe(code, timeout=EXECUTION_TIMEOUT):
    """
    Executes user Python code in a subprocess.
    Returns: { success, output, stderr, error_type?, error_message?, line? }
    """
    try:
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(code)
            tmp_path = f.name

        try:
            result = subprocess.run(
                [sys.executable, tmp_path],
                capture_output=True,
                text=True,
                timeout=timeout,
                cwd=os.path.dirname(tmp_path),
            )
        finally:
            try:
                os.unlink(tmp_path)
            except OSError:
                pass

        stdout = result.stdout or ""
        stderr = result.stderr or ""

        if result.returncode == 0:
            return {
                "success": True,
                "output": stdout,
                "stderr": stderr,
            }
        else:
            return {
                "success": False,
                "output": stdout,
                "stderr": stderr,
                "returncode": result.returncode,
            }

    except subprocess.TimeoutExpired:
        return {
            "success": False,
            "output": "",
            "stderr": "Execution timed out.",
            "error_type": "TimeoutError",
            "error_message": "Execution timed out.",
            "line": None,
        }
    except Exception as e:
        return {
            "success": False,
            "output": "",
            "stderr": str(e),
            "error_type": type(e).__name__,
            "error_message": str(e),
            "line": None,
        }
