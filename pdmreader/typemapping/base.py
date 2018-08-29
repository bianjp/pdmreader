import re
from abc import ABC, abstractmethod
from typing import List, Dict


class Converter(ABC):
    @abstractmethod
    def matches(self, data_type: str) -> bool:
        pass

    @abstractmethod
    def convert(self, data_type: str) -> str:
        pass


class PatternConverter(Converter):
    def __init__(self, pattern: str, replacement: str):
        self.pattern = re.compile(pattern, re.IGNORECASE)
        self.replacement = replacement

    def matches(self, data_type: str) -> bool:
        return self.pattern.fullmatch(data_type) is not None

    def convert(self, data_type: str) -> str:
        return self.pattern.sub(self.replacement, data_type)


class SamePatternConverter(Converter):
    def __init__(self, pattern: str):
        self.pattern = re.compile(pattern, re.IGNORECASE)

    def matches(self, data_type: str) -> bool:
        return self.pattern.fullmatch(data_type) is not None

    def convert(self, data_type: str) -> str:
        return data_type


class TypeMapper(ABC):
    def __init__(self, source: str, target: str, type_map: Dict[str, str] = None, converters: List[Converter] = None):
        """
        :param source: Source database type
        :param target: Target database type
        :param type_map: Predefined constant type map
        :param converters: Dynamic type converters
        """
        self.source = source
        self.target = target
        self.type_map: Dict[str, str] = type_map or {}
        self.converters: List[Converter] = converters or []

    def convert(self, data_type: str) -> str:
        if data_type in self.type_map:
            return self.type_map[data_type]

        for converter in self.converters:
            if converter.matches(data_type):
                result = converter.convert(data_type)
                self.type_map[data_type] = result
                return result

        return data_type
