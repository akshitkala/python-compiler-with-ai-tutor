import traceback
import re

def parse_error(exception_obj):
    """Extracts structured info from an exception object (legacy, for exec-based flow)."""
    if exception_obj is None:
        return None
    return {
        "type": type(exception_obj).__name__,
        "message": str(exception_obj),
        "details": traceback.format_exc(),
        "line": _extract_line_from_traceback(traceback.format_exc()),
    }


def parse_error_from_stderr(stderr_text):
    """
    Parses Python traceback from subprocess stderr.
    Returns: { type, message, details, line } or None if unparseable.
    """
    if not stderr_text or not stderr_text.strip():
        return None

    details = stderr_text.strip()
    line = _extract_line_from_traceback(details)

    # Match last line: "ErrorType: error message"
    last_line_match = re.search(r"^(\w+(?:Error|Exception)):\s*(.+)$", details, re.MULTILINE)
    if last_line_match:
        return {
            "type": last_line_match.group(1),
            "message": last_line_match.group(2).strip(),
            "details": details,
            "line": line,
        }

    # Fallback: use first line or whole text
    lines = details.strip().split("\n")
    return {
        "type": "RuntimeError",
        "message": lines[-1] if lines else details,
        "details": details,
        "line": line,
    }


def _extract_line_from_traceback(tb_text):
    """Extract line number from traceback (e.g. '  File "foo.py", line 3')."""
    m = re.search(r'File "[^"]+", line (\d+)', tb_text)
    return int(m.group(1)) if m else None
