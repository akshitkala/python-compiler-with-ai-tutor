import sys
import contextlib
import io
import traceback

@contextlib.contextmanager
def captured_output():
    new_out, new_err = io.StringIO(), io.StringIO()
    old_out, old_err = sys.stdout, sys.stderr
    try:
        sys.stdout, sys.stderr = new_out, new_err
        yield sys.stdout, sys.stderr
    finally:
        sys.stdout, sys.stderr = old_out, old_err

def execute_safe(code):
    """
    Executes code using exec() to allow introspection of exceptions.
    Returns structured dict matching app.py expectations.
    """
    # Basic restricted globals for 'safety'
    safe_globals = {"__builtins__": __builtins__}
    safe_locals = {}
    
    try:
        with captured_output() as (out, err):
            exec(code, safe_globals, safe_locals)
        return {
            "success": True,
            "output": out.getvalue()
        }
    except Exception as e:
        # We catch the exception to return it for analysis
        return {
            "success": False,
            "output": "",
            "exception": e
        }
