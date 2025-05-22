def clamp(value, min_value, max_value):
    if max_value == 0 and min_value == 0:
        return value
    return max(min_value, min(value, max_value))