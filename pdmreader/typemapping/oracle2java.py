import re
from typing import List

from .base import Converter, TypeMapper


class Oracle2JavaTypeMapper(TypeMapper):
    def __init__(self):
        type_map = {
            'date': 'Date',
            'integer': 'Integer',
            'double': 'Double',
            'double precision': 'Double',
            'int': 'Integer',
            'long raw': 'Blob',
            'number': 'Double',
            'real': 'Double',
            'smallint': 'Integer',
        }
        converters: List[Converter] = [
            NumberConverter(),
            FallbackConverter(),
        ]
        super().__init__('oracle', 'java', type_map, converters)


class NumberConverter(Converter):
    pattern = re.compile(r'(?:number|numberic)\s*\((\d+)(?:,\s*(\d+))?\)', re.IGNORECASE)

    def matches(self, data_type: str) -> bool:
        return self.pattern.fullmatch(data_type) is not None

    def convert(self, data_type: str) -> str:
        m = self.pattern.fullmatch(data_type)
        precision = int(m.group(1))
        scale = int(m.group(2)) if m.group(2) else None

        if scale is None or scale == 0:
            if precision < 10:
                return 'Integer'
            elif precision < 19:
                return 'Long'
            else:
                return 'BigInteger'
        else:
            return 'Double'


# All unknown types fallback to String
class FallbackConverter(Converter):
    def matches(self, data_type: str) -> bool:
        return True

    def convert(self, data_type: str) -> str:
        return 'String'
