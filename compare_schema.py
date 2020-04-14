from typing import List, Dict, Tuple
from xml.etree import ElementTree
from xml.etree.ElementTree import Element
import cx_Oracle

from pdmreader.parser import PDMParser, Column, find_nodes, find_text


def get_tables(connection) -> List[str]:
    cursor = connection.cursor()
    cursor.execute("""
        SELECT LOWER(table_name) 
        FROM user_tables 
        WHERE table_name LIKE 'OC\_%' ESCAPE '\\' ORDER BY LOWER(table_name)
    """)
    rows = cursor.fetchall()
    tables = [row[0].lower() for row in rows]
    cursor.close()
    return tables


def get_columns(cursor, table: str) -> List[Column]:
    cursor.execute("""
        SELECT LOWER(column_name), LOWER(data_type), data_length, data_precision, data_scale, nullable
        FROM user_tab_columns 
        WHERE table_name = :t
        """, t=table.upper())
    rows = cursor.fetchall()

    columns = []
    for row in rows:
        name: str = row[0].lower()
        data_type: str = row[1].lower()
        length = row[2]
        precision = row[3]
        scale = row[4]
        required = row[5] == 'Y'

        c = Column(name=name, code=name, data_type=data_type,
                   length=length, precision=precision, scale=scale,
                   required=required, comment='', id='')
        columns.append(c)

    return columns


def parse_db_schema(connection) -> Dict[str, List[Column]]:
    db_tables = get_tables(connection)
    schema = {}

    cursor = connection.cursor()
    for table in db_tables:
        schema[table] = get_columns(cursor, table)
    cursor.close()
    return schema


def parse_pdm_schema(path: str) -> Tuple[Dict[str, List[Column]], PDMParser]:
    parser = PDMParser(path)
    schema = parser.parse()
    result = {}

    for table in schema.tables:
        if table.code.startswith('oc_'):
            result[table.code] = table.columns

    return result, parser


def main():
    connection = cx_Oracle.connect('ord', 'bss3', '10.45.46.11/orcl')
    db_schema = parse_db_schema(connection)
    connection.close()
    pdm_schema, pdm_parser = parse_pdm_schema('/home/bianjp/repos/ztesoft/BSS3Documents/oc/数据模型/oc_core_om_oc_oracle.pdm')

    db_schema.keys()
    missing_tables = list(set(db_schema.keys()) - set(pdm_schema.keys()))
    extra_tables = list(set(pdm_schema.keys()) - set(db_schema.keys()))

    if len(missing_tables) > 0 or len(extra_tables) > 0:
        if len(missing_tables) > 0:
            missing_tables.sort()
            print("Missing tables: " + ", ".join(missing_tables))
        if len(extra_tables) > 0:
            extra_tables.sort()
            print("Extra tables: " + ", ".join(extra_tables))
        print()
        print()

    tables = [t for t in db_schema if t in pdm_schema]
    for table in tables:
        db_column_names = [c.code for c in db_schema[table]]
        pdm_column_names = [c.code for c in pdm_schema[table]]

        missing_columns = [c for c in db_column_names if c not in pdm_column_names]
        extra_columns = [c for c in pdm_column_names if c not in db_column_names]
        common_column_names = [c for c in db_column_names if c not in missing_columns]
        incompatible_columns = []

        for column in common_column_names:
            db_c = next(c for c in db_schema[table] if c.code == column)
            pdm_c = next(c for c in pdm_schema[table] if c.code == column)
            if db_c.data_type_str != pdm_c.data_type_str:
                if db_c.data_type_str == pdm_c.data_type_str + ' NOT NULL':
                    pdm_parser.set_column_mandatory(pdm_c.id)
                    continue
                elif db_c.data_type_str + ' NOT NULL' == pdm_c.data_type_str:
                    pdm_parser.remove_column_mandatory(pdm_c.id)
                    continue
                incompatible_columns.append((db_c, pdm_c))

        pdm_parser.save()
        if len(missing_columns) > 0 or len(extra_columns) > 0 or len(incompatible_columns) > 0:
            print("{}:".format(table))
            if len(missing_columns) > 0:
                missing_columns.sort()
                print("Missing: " + ", ".join(missing_columns))
            if len(extra_columns) > 0:
                extra_columns.sort()
                print("Missing: " + ", ".join(extra_columns))

            if len(incompatible_columns) > 0:
                incompatible_columns.sort(key=lambda p: p[0].code)
                print("Incompatible:")
                for pair in incompatible_columns:
                    print("  {:>20s}: {:30s}{:30s}".format(pair[0].code, pair[0].data_type_str, pair[1].data_type_str))

            print()


if __name__ == '__main__':
    main()
