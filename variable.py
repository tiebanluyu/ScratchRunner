def safe_int(object) -> int:
    if type(object)==int:
        return object
    try:
        return int(object)
    except:
        return 0
def safe_str(object) -> str:
    if type(object)==str:
        return object
    try:
        return str(object)
    except:
        return ""    