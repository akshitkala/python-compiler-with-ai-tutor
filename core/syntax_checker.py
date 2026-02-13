import ast

def check_syntax(code):
    """Returns None if valid, else dict with message and line."""
    try:
        ast.parse(code)
        return None
    except SyntaxError as e:
        return {"message": e.msg, "line": e.lineno}
