from typing import List

from .base import Converter, PatternConverter, TypeMapper


# https://docs.oracle.com/en/database/oracle/oracle-database/18/sqlrf/Data-Types.html#GUID-A3C0D836-BADB-44E5-A5D4-265BA5968483
# https://dev.mysql.com/doc/refman/8.0/en/data-types.html
# https://docs.oracle.com/cd/E12151_01/doc.150/e12155/oracle_mysql_compared.htm
class MySQL2OracleTypeMapper(TypeMapper):
    def __init__(self):
        type_map = {
            'bigint': 'number(19)',
            'bit': 'raw',
            'blob': 'blob',
            'char': 'char',
            'date': 'date',
            'datetime': 'date',
            'decimal': 'number',
            'double': 'binary_double',
            'double precision': 'binary_double',
            'enum': 'varchar2',
            'float': 'binary_float',
            'int': 'number(10)',
            'integer': 'number(10)',
            'longblob': 'blob',
            'longtext': 'clob',
            'mediumblob': 'blob',
            'mediumint': 'number(7)',
            'mediumtext': 'clob',
            'numeric': 'number',
            'real': 'binary_double',
            'set': 'varchar2',
            'smallint': 'number(5)',
            'text': 'clob',
            'time': 'date',
            'timestamp': 'date',
            'tinyblob': 'raw',
            'tinyint': 'number(3)',
            'tinytext': 'varchar2',
            'varchar': 'varchar2',
            'year': 'number',
        }

        converters: List[Converter] = [
            PatternConverter(r'varchar\((\d+)\)', r'varchar2(\1)'),
            PatternConverter(r'varchar\((\d+)\)', r'nvarchar2(\1)'),
            PatternConverter(r'char\((\d+)\)', r'nchar(\1)'),
            PatternConverter(r'decimal\((.*)\)', r'number(\1)'),
        ]
        super().__init__('mysql', 'oracle', type_map, converters)
