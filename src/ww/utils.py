

def ensure_tuple(val):
    if not isinstance(val, str):
        try:
            return tuple(val)
        except TypeError:
            return (val,)
    return (val,)
