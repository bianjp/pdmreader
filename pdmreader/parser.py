import dataclasses
from typing import List, Optional
from xml.etree import ElementTree
from xml.etree.ElementTree import Element

from .models import Column, Key, Index, Table, Sequence, Schema

namespaces = {
    'a': 'attribute',
    'c': 'collection',
    'o': 'object',
}


def find_text(node: Element, path: str, lowercase: bool = True) -> str:
    text = node.findtext(path, '', namespaces).strip()
    if lowercase:
        text = text.lower()
    return text


def find_nodes(node: Element, path: str) -> List[Element]:
    nodes: List[Element] = node.findall(path, namespaces)
    return nodes or []


class TableParser:
    def __init__(self, table_node: Element):
        self.table_node = table_node
        self.table_id: str = table_node.attrib['Id']
        self.table_name = find_text(table_node, 'a:Name')
        self.table_code = find_text(table_node, 'a:Code')
        self.table_comment = find_text(table_node, 'a:Comment', False)
        if self.table_name == self.table_code:
            self.table_name = ''

    def parse(self) -> Table:
        columns = self.parse_columns()
        keys = self.parse_keys(columns)
        primary_key = self.parse_primary_key(keys)
        indexes = self.parse_indexes(columns)

        table = Table(id=self.table_id, name=self.table_name, code=self.table_code, comment=self.table_comment,
                      columns=columns,
                      keys=keys, primary_key=primary_key, indexes=indexes)
        return table

    def parse_columns(self) -> List[Column]:
        column_nodes = find_nodes(self.table_node, 'c:Columns/o:Column')
        columns: List[Column] = []
        for column_node in column_nodes:
            column_id = column_node.attrib['Id']
            name = find_text(column_node, 'a:Name')
            code = find_text(column_node, 'a:Code')
            comment = find_text(column_node, 'a:Comment', False)
            data_type = find_text(column_node, 'a:DataType')
            length = find_text(column_node, 'a:Length')
            required = find_text(column_node, 'a:Column.Mandatory') == '1'

            if name == code:
                name = ''

            column = Column(id=column_id, name=name, code=code, required=required, comment=comment,
                            data_type=data_type, length=length)
            columns.append(column)

        return columns

    def parse_keys(self, columns: List[Column]) -> List[Key]:
        keys: List[Key] = []
        nodes = find_nodes(self.table_node, 'c:Keys/o:Key')
        for node in nodes:
            key_id: str = node.attrib['Id']
            name = find_text(node, 'a:Name')
            code = find_text(node, 'a:ConstraintName')

            key_columns: List[Column] = []
            column_nodes = find_nodes(node, 'c:Key.Columns/o:Column')
            for column_node in column_nodes:
                ref = column_node.attrib['Ref']
                column = next((c for c in columns if c.id == ref), None)
                if not column:
                    raise Exception("Unknown column in key: key={}, ref={}".format(key_id, ref))
                key_columns.append(column)

            if len(key_columns) == 0:
                continue

            if not code:
                code = 'uk_' + '_'.join([c.code for c in key_columns]) + self.table_code

            key = Key(id=key_id, code=code, name=name, columns=key_columns)
            keys.append(key)

        return keys

    def parse_primary_key(self, keys: List[Key]) -> Optional[Key]:
        if len(keys) == 0:
            return None

        nodes = find_nodes(self.table_node, 'c:PrimaryKey/o:Key')
        if len(nodes) != 1:
            raise Exception("Unexpected number of keys in primary key")

        ref: str = nodes[0].attrib['Ref']
        key = next((k for k in keys if k.id == ref), None)
        if not key:
            raise Exception("Unknown primary key: ref={}".format(ref))

        # Remove from key list
        keys.remove(key)

        # Force constraint name for primary key
        code = 'pk_' + self.table_code.lower()
        primary_key = dataclasses.replace(key, code=code)

        return primary_key

    def parse_indexes(self, columns: List[Column]) -> List[Index]:
        indexes: List[Index] = []
        nodes = find_nodes(self.table_node, 'c:Indexes/o:Index')
        for node in nodes:
            if len(find_nodes(node, 'c:LinkedObject/o:Key')) > 0:
                continue

            index_id: str = node.attrib['Id']
            name = find_text(node, 'a:Name')
            code = find_text(node, 'a:Code')
            unique = find_text(node, 'a:Unique') == '1'

            index_columns: List[Column] = []
            column_nodes = find_nodes(node, 'c:IndexColumns/o:IndexColumn/c:Column/o:Column')
            for column_node in column_nodes:
                ref = column_node.attrib['Ref']
                column = next((c for c in columns if c.id == ref), None)
                if not column:
                    raise Exception("Unknown column in index: index={}, ref={}".format(index_id, ref))
                index_columns.append(column)

            if len(index_columns) == 0:
                continue

            if not code:
                code = ('uk_' if unique else 'idx_') + '_'.join([c.code for c in index_columns]) + self.table_code

            index = Index(id=index_id, code=code, name=name, unique=unique, columns=index_columns)
            indexes.append(index)

        return indexes


class PDMParser:
    def __init__(self, file: str):
        tree: ElementTree = ElementTree.parse(file)
        self.root = tree.getroot()

    def parse(self) -> Schema:
        db = self.detect_database_type()
        sequences = self.parse_sequences()
        tables = self.parse_tables()
        schema = Schema(db, tables, sequences)
        return schema

    def detect_database_type(self) -> str:
        text = find_text(self.root, 'o:RootObject/c:Children/o:Model/c:TargetModels/o:TargetModel/a:Name', True)
        if 'mysql' in text:
            return 'mysql'
        elif 'oracle' in text:
            return 'oracle'
        else:
            raise Exception('Unsupported database type: ' + text)

    def parse_tables(self) -> List[Table]:
        table_nodes = find_nodes(self.root, 'o:RootObject/c:Children/o:Model/c:Tables/o:Table')
        tables: List[Table] = []

        for table_node in table_nodes:
            table = TableParser(table_node).parse()
            tables.append(table)

        # sort by code
        tables.sort(key=lambda t: t.code)

        return tables

    def parse_sequences(self):
        seq_nodes = find_nodes(self.root, 'o:RootObject/c:Children/o:Model/c:Sequences/o:Sequence')
        sequences: List[Sequence] = []

        for seq_node in seq_nodes:
            seq_code = find_text(seq_node, 'a:Code')
            sequences.append(Sequence(seq_code))

        # sort by code
        sequences.sort(key=lambda t: t.code)

        return sequences
