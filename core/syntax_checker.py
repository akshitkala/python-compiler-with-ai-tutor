import ast

def check_syntax(code):
    try:
        ast.parse(code)
        return None
    except SyntaxError as e:
        return f"SyntaxError (line {e.lineno}): {e.msg}"
