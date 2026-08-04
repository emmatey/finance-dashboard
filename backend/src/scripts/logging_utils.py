LOG_FULL_DATA = False  # set True to log complete param lists and result sets without truncation


def fmt_data(data, limit: int = 10) -> str:
    """
    Truncate list/tuple-like data for logging: shows the first `limit` items
    plus a count of the rest, so a single log line never balloons with a
    large payload (e.g. hundreds of query params or rejected screener symbols).
    """
    if LOG_FULL_DATA or not hasattr(data, '__len__') or len(data) <= limit:
        return repr(data)
    return f"{repr(data[:limit])[:-1]}, ... (+{len(data) - limit} more)"
