import json
from ValueEnum import ValueEnum


class EnumEncoder(json.JSONEncoder):
    def default(self, obj):
        if obj in ValueEnum:
            return {'__enum__': str(obj)}
        return json.JSONEncoder.default(self, obj)


def as_enum(data):
    if '__enum__' in data:
        name, member = data['__enum__'].split('.')
        return getattr(ValueEnum, member)
    else:
        return data