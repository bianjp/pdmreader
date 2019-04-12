from dataclasses import dataclass
from typing import List, Optional
import re


class TypeUtil:
    numeric_types = ('number', 'numeric', 'float', 'double', 'integer', 'decimal')
    string_types = ('char', 'clob')

    @staticmethod
    def is_numeric(data_type):
        for type_keyword in TypeUtil.numeric_types:
            if type_keyword in data_type:
                return True

        return False

    @staticmethod
    def is_string(data_type):
        for type_keyword in TypeUtil.string_types:
            if type_keyword in data_type:
                return True

        return False


@dataclass
class DataType:
    name: str
    length: Optional[str] = None
    precision: Optional[str] = None
    scale: Optional[str] = None

    def __expr__(self):
        if self.is_numeric():
            if self.precision and self.scale:
                return '{}({},{})'.format(self.name, self.precision, self.scale)
            elif self.precision:
                return '{}({})'.format(self.name, self.precision)
        elif self.is_string():
            if self.length:
                return '{}({})'.format(self.name, self.length)

        return self.name

    def __str__(self):
        return self.__expr__()

    def is_numeric(self):
        return TypeUtil.is_numeric(self.name)

    def is_string(self):
        return TypeUtil.is_string(self.name)


@dataclass
class Column:
    id: str
    name: str
    code: str
    required: bool
    comment: str
    data_type: DataType


@dataclass
class Key:
    id: str
    code: str
    name: str
    columns: List[Column]


@dataclass
class Index:
    id: str
    code: str
    name: str
    unique: bool
    columns: List[Column]


@dataclass
class Table:
    id: str
    name: str
    code: str
    comment: str
    columns: List[Column]
    keys: List[Key]  # unique keys (primary key excluded)
    primary_key: Optional[Key]
    indexes: List[Index]


@dataclass
class Sequence:
    code: str


@dataclass
class Schema:
    db: str  # mysql/oracle
    tables: List[Table]
    sequences: List[Sequence]
