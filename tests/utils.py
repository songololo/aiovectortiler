import ujson


def copy(d):
    return ujson.loads(ujson.dumps(d))
