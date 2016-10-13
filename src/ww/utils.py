# TODO: add "removable_property" we use in tygs
# TODO: add reify, based on removable property


def ensure_tuple(val):
    if not isinstance(val, str):
        try:
            return tuple(val)
        except TypeError:
            return (val,)
    return (val,)
