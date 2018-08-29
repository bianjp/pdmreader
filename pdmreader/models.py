from dataclasses import dataclass
from typing import List, Optional


@dataclass
class Column:
    id: str
    name: str
    code: str
    required: bool
    comment: str
    data_type: str
    length: str


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
