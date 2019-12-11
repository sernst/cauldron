import flask


def from_request(request=None) -> dict:
    """ Fetches the arguments for the current Flask application request."""
    request = request if request else flask.request

    try:
        json_args = request.get_json(silent=True)
    except Exception:
        json_args = None

    try:
        get_args = request.values
    except Exception:
        get_args = None

    return next(a for a in [json_args, get_args, {}] if a is not None)
