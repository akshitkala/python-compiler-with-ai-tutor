import traceback

def parse_error(exception_obj):
    """
    Extracts structured info from an exception object.
    """
    if exception_obj is None:
        return None
        
    stack = traceback.extract_tb(exception_obj.__traceback__)
    # We care about the last frame usually, or the one in the user code string
    # Since we use exec, we might need to filter frames.
    
    # Simple extraction for now
    return {
        "type": type(exception_obj).__name__,
        "message": str(exception_obj),
        "details": traceback.format_exc()
    }
