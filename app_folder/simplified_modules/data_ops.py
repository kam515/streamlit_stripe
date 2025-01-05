import json
from pydantic import BaseModel

def to_nested_dict(obj):
    """
    Convert Pydantic models, lists, and dicts to nested dicts.
    """
    if isinstance(obj, BaseModel):
        data = obj.model_dump()
        return {k: to_nested_dict(v) for k, v in data.items()}
    elif isinstance(obj, list):
        return [to_nested_dict(item) for item in obj]
    elif isinstance(obj, dict):
        return {k: to_nested_dict(v) for k, v in obj.items()}
    return obj

def to_json(obj):
    """
    Return JSON string from nested dict form.
    """
    return json.dumps(to_nested_dict(obj), indent=2)
