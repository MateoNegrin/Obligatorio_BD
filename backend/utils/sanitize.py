import re

def formatDate(v):
    try:
        import datetime
        if isinstance(v, (datetime.date, datetime.time, datetime.datetime)):
            return v.isoformat()
    except Exception:
        pass
    return v

def sanitize_input(s: str):
    if not isinstance(s, str):
        return s
    return re.sub(r"[\'\"`;%#\\]", "", s)

def sanitize_fields(data: dict, field_names):
    for k in field_names:
        if k in data and isinstance(data[k], str):
            data[k] = sanitize_input(data[k])