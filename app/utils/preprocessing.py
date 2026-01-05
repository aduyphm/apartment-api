import unidecode
import re


def __cast_num_type__(x):
    try:
        return float(x)
    except:
        return -1


def __cast_cat_type__(x):
    x = str(x)
    x = unidecode.unidecode(x)
    x = x.upper().strip()
    x = re.sub(r"\s+", "-", x)
    if len(x) == 0 or len(x) > 50:
        return "MISSING"
    else:
        return x
