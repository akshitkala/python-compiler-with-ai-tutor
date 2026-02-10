def format_response(status, data=None, error=None):
    """
    Standardized API response format.
    """
    return {
        "status": status,
        "data": data,
        "error": error
    }
