from functools import wraps

from flask import request, abort


def get_params_from_request(key, cast=None):
    value = request.args.get(key)
    if value is None:
        return None
    if cast:
        try:
            return cast(value)
        except TypeError:
            return None
        except ValueError:
            return None
    else:
        return value


def local_only(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if request.remote_addr == '127.0.0.1':
            return f(*args, **kwargs)
        else:
            print('Rejected connection from {}'.format(request.remote_addr))
            abort(403)
    return wrapper
