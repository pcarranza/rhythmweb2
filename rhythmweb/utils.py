def to_int(value, message):
    return cast(value, message, int)


def to_float(value, message):
    return cast(value, message, float)


def cast(value, message, func):
    if value is None:
        return None
    try:
        return func(value)
    except:
        raise ValueError(message)
    
def to_list(value):
    if type(value) is list:
        return value
    return [value]
