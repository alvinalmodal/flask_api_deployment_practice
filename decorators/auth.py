from functools import wraps

from flask import abort, request


def auth_sample(func):
    @wraps(func)
    def inner(*args, **kwargs):
        query_params = request.args.to_dict()
        if query_params.get("apiKey") is None or query_params.get("apiKey") == "":
            abort(401)
        result = func(*args, **kwargs)
        return result
    return inner