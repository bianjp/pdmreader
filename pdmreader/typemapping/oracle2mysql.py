import re
from typing import List

from .base import Converter, PatternConverter, SamePatternConverter, TypeMapper


# https://docs.oracle.com/en/database/oracle/oracle-database/18/sqlrf/Data-Types.html#GUID-A3C0D836-BADB-44E5-A5D4-265BA5968483
# https://dev.mysql.com/doc/refman/8.0/en/data-types.html
# https://www.convert-in.com/docs/ora2sql/types-mapping.htm
class Oracle2MySQLTypeMapper(TypeMapper):
    def __init__(self):
        type_map = {
            'bfile': 'varchar(255)',
            'blob': 'longblob',
            'clob': 'longtext',
            'date': 'datetime',
            'double precision': 'double precision',
            'integer': 'int',
            'int': 'int',
            'long': 'longtext',
            'long raw': 'longblob',
            'nclob': 'nvarchar(max)',
            'number': 'double',
            'real': 'double',
            'rowid': 'char(10)',
            'smallint': 'decimal(38)',
            'xmltype': 'longtext',
        }
        converters: List[Converter] = [
            PatternConverter(r'varchar2?\((\d+)( byte)?\)', r'varchar(\1)'),
            PatternConverter(r'nvarchar2\((\d+)( byte)?\)', r'nvarchar(\1)'),
            SamePatternConverter(r'nchar varying\((\d+)\)'),
            SamePatternConverter(r'numeric\((.*)\)'),
            PatternConverter(r'float(\(\d+\))?', 'double'),
            NumberConverter(),
            PatternConverter(r'timestamp\((\d*)\)', r'datetime(\1)'),
            PatternConverter(r'timestamp\((\d*)\) with time zone', r'datetime(\1)'),
            PatternConverter(r'interval year\(\d*\) to month', 'varchar(30)'),
            PatternConverter(r'interval day\(\d*\) to seconds?', 'varchar(30)'),
            PatternConverter(r'urowid\((\d+)\)', r'varchar(\1)'),
            RawConverter(),
        ]
        super().__init__('oracle', 'mysql', type_map, converters)


class NumberConverter(Converter):
    pattern = re.compile(r'number\s*\((\d+)(?:,\s*(\d+))?\)', re.IGNORECASE)

    def matches(self, data_type: str) -> bool:
        return self.pattern.fullmatch(data_type) is not None

    def convert(self, data_type: str) -> str:
        m = self.pattern.fullmatch(data_type)
        precision = int(m.group(1))
        scale = int(m.group(2)) if m.group(2) else None

        if scale is None or scale == 0:
            if precision < 3:
                return 'tinyint'
            elif precision < 5:
                return 'smallint'
            elif precision < 10:
                return 'int'
            elif precision < 19:
                return 'bigint'
            else:
                return 'decimal({})'.format(precision)
        else:
            return "decimal({}, {})".format(precision, scale)


class CharacterConverter(Converter):
    char_pattern = re.compile(r'(?:char|character)\((\d+)\)', re.IGNORECASE)
    nchar_pattern = re.compile(r'nchar\((\d+)\)', re.IGNORECASE)

    def matches(self, data_type: str) -> bool:
        return self.char_pattern.fullmatch(data_type) is not None or self.nchar_pattern.fullmatch(data_type) is not None

    def convert(self, data_type: str) -> str:
        m = self.char_pattern.fullmatch(data_type)
        if m:
            size = int(m.group(1))
            if size < 256:
                return 'char({})'.format(size)
            else:
                return 'varchar({})'.format(size)

        m = self.nchar_pattern.fullmatch(data_type)
        if m:
            size = int(m.group(1))
            if size < 256:
                return 'nchar({})'.format(size)
            else:
                return 'nvarchar({})'.format(size)


class RawConverter(Converter):
    pattern = re.compile(r'raw\((\d+)\)', re.IGNORECASE)

    def matches(self, data_type: str) -> bool:
        return self.pattern.fullmatch(data_type) is not None

    def convert(self, data_type: str) -> str:
        m = self.pattern.fullmatch(data_type)
        size = int(m.group(1))
        if size < 256:
            return 'binary({})'.format(size)
        else:
            return 'varbinary({})'.format(size)
