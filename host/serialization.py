from abc import ABC, abstractmethod
from collections.abc import Iterable, Mapping
import inspect

# TODO automate this so it doesn't have to be explicitly defined and can be called recursively
class GameSerializable(ABC):
    @abstractmethod
    def to_json(self) -> dict:
        pass
    
    @classmethod
    @abstractmethod
    def from_json(cls, json_data: dict):
        pass

def serialize_to_json(obj):
    if isinstance(obj, (int, float, str, bool, type(None))):
        return obj
    elif isinstance(obj, dict):
        return {k: serialize_to_json(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [serialize_to_json(x) for x in obj]
    elif hasattr(obj, '__dict__'):
        return serialize_to_json(obj.__dict__)
    elif isinstance(obj, Iterable):
        return [serialize_to_json(x) for x in obj]
    else:
        return str(obj)
    
def deserialize_from_json(data, cls):
    if not isinstance(data, Mapping):
        return data

    init_signature = inspect.signature(cls.__init__)
    init_params = init_signature.parameters

    ctor_args = {}
    for name, param in init_params.items():
        if name == 'self':
            continue
        if name == 'field':
            pass
        if name in data:
            if inspect.isclass(param.annotation) and isinstance(data[name], dict):
                ctor_args[name] = deserialize_from_json(data[name], param.annotation)
            elif (isinstance(param.annotation, list) and param.annotation and
                  isinstance(param.annotation[0], type) and isinstance(data[name], list)):
                ctor_args[name] = [deserialize_from_json(item, param.annotation[0]) for item in data[name]]
            else:
                ctor_args[name] = data[name]

    return cls(**ctor_args)

