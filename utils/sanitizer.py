import ast

FORBIDDEN_MODULES = {'os', 'sys', 'subprocess', 'shutil', 'importlib'}

def is_safe(code):
    """
    Checks for forbidden imports using AST.
    """
    try:
        tree = ast.parse(code)
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    if alias.name.split('.')[0] in FORBIDDEN_MODULES:
                        return False, f"Importing '{alias.name}' is forbidden."
            elif isinstance(node, ast.ImportFrom):
                if node.module and node.module.split('.')[0] in FORBIDDEN_MODULES:
                    return False, f"Importing from '{node.module}' is forbidden."
        return True, None
    except SyntaxError:
        # Syntax errors are handled by syntax_checker, not sanitizer
        return True, None
