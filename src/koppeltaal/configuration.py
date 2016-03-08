import threading

_thread_local = threading.local()


def set_url_function(func):
    _thread_local.url_function = func


def url(context, *args, **kw):
    func = getattr(_thread_local, 'url_function', None)
    if func is None:
        return str(context)
    res = func(context, *args, **kw)
    return res


def set_identity_function(func):
    _thread_local.identity_function = func


def identity(context, *args, **kw):
    func = getattr(_thread_local, 'identity_function', None)
    if func is None:
        return str(id(context))
    res = func(context, *args, **kw)
    return res