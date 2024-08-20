import logging
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
        logging.debug("触发保护 "+str(object))
         
        return 0.0         
# 输入参数 str 需要判断的字符串
# 返回值   True：该字符串为浮点数；False：该字符串不是浮点数。
def IsNum(str):
    s=str.split('.')
    if len(s)>2:
        return False
    else:
        for si in s:
            if not si.isdigit():
                return False
        return True    