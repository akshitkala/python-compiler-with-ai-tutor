def analyze_error(error_type, error_message):
    """
    Maps error types/messages to internal concepts.
    """
    # Simple rule-based mapping (can be expanded)
    if "NameError" in error_type:
        return "VARIABLE_NOT_DEFINED"
    elif "IndexError" in error_type:
        return "LIST_INDEX_OUT_OF_RANGE"
    elif "TypeError" in error_type:
        return "TYPE_MISMATCH"
    elif "SyntaxError" in error_type:
        return "SYNTAX_ERROR"
    else:
        return "UNKNOWN_ERROR"
