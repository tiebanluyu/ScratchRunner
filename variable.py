def safe_int(object) -> int:
    if type(object)==int:
        return object
    try:
        return int(object)
    except:
        try:
            return int(float(object))# int("100.0")
        except:
            return 0
def safe_str(object) -> str:
    if type(object)==str:
        return object
    try:
        return str(object)
    except:
        return ""   
def safe_bool(object) -> bool:
    if type(object)==bool:
        return object
    try:
        return bool(object)
    except:
        return False     
def safe_float(object) -> float:
    if type(object)==float:
        return object
    try:
        return float(object)
    except:
        #logging.debug("hello")
        return 0.0         