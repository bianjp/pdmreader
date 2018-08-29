from .base import TypeMapper
from .mysql2oracle import MySQL2OracleTypeMapper
from .oracle2java import Oracle2JavaTypeMapper
from .oracle2mysql import Oracle2MySQLTypeMapper


# Convert types between databases
class TypeMapping:
    mappers = [
        Oracle2MySQLTypeMapper(),
        MySQL2OracleTypeMapper(),
        Oracle2JavaTypeMapper(),
    ]

    @classmethod
    def convert(cls, source_db: str, target_db: str, data_type: str):
        """
        Convert a type in source database to an appropriate data type in target database.

        :param source_db: Source database type
        :param target_db: Target database type
        :param data_type: Data type to convert
        :return: An appropriate data type in target database. Return the original data type if failed to convert.
        """
        if source_db == target_db:
            return data_type

        for mapper in cls.mappers:
            if mapper.source == source_db and mapper.target == target_db:
                return mapper.convert(data_type)

        return data_type
