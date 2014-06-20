
def to_int(value, message):
    if value is None:
        return None
    try:
        return int(value)
    except:
        raise ValueError(message)
