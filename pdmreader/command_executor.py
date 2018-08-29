import fnmatch
import re
from typing import List

from .models import Column, Table, Sequence, Schema
from .typemapping import TypeMapping
from .unicode_formatter import UnicodeFormatter


class CommandExecutor:
    whitespace_pattern = re.compile('\s+')

    def __init__(self, schema: Schema):
        self.schema = schema
        self.formatter = UnicodeFormatter()
        self.horizontal_output = True
        print('DB: {}'.format(self.schema.db))
        print('Tables: {}'.format(len(self.schema.tables)))
        print('Sequences: {}'.format(len(self.schema.sequences)))

    def command(self, command: str):
        command = self.collapse_whitespace(command)
        if command == 'help':
            self.print_help()
        elif command == 'exit':
            raise EOFError()
        elif command == 't':
            self.toggle_output()
        elif command == 'tables':
            self.print_tables()
        elif command == 'seq':
            self.print_sequences()
        elif command.startswith('seq '):
            self.print_sequences(command.split()[1])
        elif command.startswith('tables '):
            self.print_tables(command.split()[1])
        elif command.startswith('table '):
            self.print_table(command.split()[1])
        elif command.startswith('mysql '):
            self.print_table_ddl('mysql', command.split()[1])
        elif command.startswith('oracle '):
            self.print_table_ddl('oracle', command.split()[1])
        elif command.startswith('java '):
            self.print_table_ddl('java', command.split()[1])
        else:
            print('Unknown command')

    def toggle_output(self):
        self.horizontal_output = not self.horizontal_output
        if self.horizontal_output:
            print('Horizontal output on')
        else:
            print('Vertical output on')

    def print_tables(self, glob: str = None):
        if glob:
            try:
                pattern = re.compile(fnmatch.translate(glob), re.IGNORECASE)
            except re.error:
                print('Invalid glob: ' + glob)
                return
            tables = [t for t in self.schema.tables if pattern.match(t.code)]
            if len(tables) <= 0:
                print('No matching table')
                return
        else:
            tables = self.schema.tables

        format_spec = '{:30s}{:40s}{:50s}'

        def print_table(t: Table):
            if self.horizontal_output:
                print(self.formatter.format(format_spec, t.code, t.name, t.comment))
            else:
                print('Code: {}'.format(t.code))
                print('Name: {}'.format(t.name))
                print('Comment: {}'.format(t.comment))
                print()

        def print_header():
            if self.horizontal_output:
                print(self.formatter.format('{:30s}{:40s}{:50s}', 'Code', 'Name', 'Comment'))
                print('-' * 80)

        print_header()
        for table in tables:
            print_table(table)

        print('Count: {}'.format(len(tables)))

    def print_table(self, table_name: str):
        if not table_name:
            print('No table specified')
            return

        table = next((t for t in self.schema.tables if t.code.lower() == table_name.lower()), None)
        if not table:
            print('Table not found: ' + table_name)
            return

        format_spec = '{:30}{:20}{:10}{:30}{}'

        def print_column(c: Column):
            if self.horizontal_output:
                print(self.formatter.format(format_spec, c.code, c.data_type, 'True' if c.required else 'False', c.name,
                                            c.comment))
            else:
                print('Code: {}'.format(c.code))
                print('Type: {}'.format(c.data_type))
                print('Required: {}'.format('True' if c.required else 'False'))
                print('Name: {}'.format(c.name))
                print('Comment: {}'.format(c.comment))
                print()

        def print_header():
            if self.horizontal_output:
                print(self.formatter.format(format_spec, 'Code', 'Type', 'Required', 'Name', 'Comment'))
                print('-' * 100)

        print_header()
        for column in table.columns:
            print_column(column)

    def print_table_ddl(self, db: str, table_name: str):
        if not table_name:
            print('No table specified')
            return

        table = next((t for t in self.schema.tables if t.code.lower() == table_name.lower()), None)
        if not table:
            print('Table not found: ' + table_name)
            return

        if db == 'mysql':
            self.print_table_ddl_mysql(table, self.schema.db)
        elif db == 'oracle':
            self.print_table_ddl_oracle(table, self.schema.db)
        elif db == 'java':
            self.print_table_ddl_java(table, self.schema.db)

    @staticmethod
    def print_table_ddl_mysql(table: Table, source_db: str):
        result = ''
        result += 'CREATE TABLE `{}` (\n'.format(table.code)
        for column in table.columns:
            result += '  `{}` {}'.format(column.code, TypeMapping.convert(source_db, 'mysql', column.data_type))
            if column.required:
                result += ' NOT NULL'
            if column.name:
                result += " COMMENT '{}'".format(column.name)
            result += ',\n'

        if table.primary_key:
            result += '  PRIMARY KEY ({}),\n'.format(CommandExecutor.quote_columns(table.primary_key.columns, '`'))

        for key in table.keys:
            result += '  UNIQUE KEY `{}`({}),\n'.format(key.code, CommandExecutor.quote_columns(key.columns, '`'))

        for index in table.indexes:
            result += '  {}KEY `{}`({}),\n'.format('UNIQUE ' if index.unique else '', index.code,
                                                   CommandExecutor.quote_columns(index.columns, '`'))

        result = result.rstrip(',\n') + '\n)'

        if table.name:
            result += " COMMENT '{}'".format(table.name)
        result += ';'

        print(result)

    @staticmethod
    def print_table_ddl_oracle(table: Table, source_db: str):
        result = ''
        result += 'CREATE TABLE "{}" (\n'.format(table.code)
        for column in table.columns:
            result += '  "{}" {}'.format(column.code, TypeMapping.convert(source_db, 'oracle', column.data_type))
            if column.required:
                result += ' NOT NULL'
            result += ',\n'

        if table.primary_key:
            result += '  CONSTRAINT "{}" PRIMARY KEY ({}),\n'.format(
                table.primary_key.code,
                CommandExecutor.quote_columns(table.primary_key.columns, '"'))

        if len(table.keys) > 0:
            for key in table.keys:
                result += '  CONSTRAINT "{}" UNIQUE ({}),\n'.format(key.code,
                                                                    CommandExecutor.quote_columns(key.columns, '"'))

        result = result.rstrip(',\n') + '\n);\n\n'

        if table.name:
            result += 'COMMENT ON TABLE "{}" IS \'{}\';\n'.format(table.code, table.name)
        for c in table.columns:
            if c.name:
                result += 'COMMENT ON COLUMN "{}"."{}" IS \'{}\';\n'.format(table.code, c.code, c.name)

        if len(table.indexes) > 0:
            for index in table.indexes:
                result += 'CREATE {}INDEX "{}" ON "{}"({});\n'.format(
                    'UNIQUE ' if index.unique else '',
                    index.code,
                    table.code,
                    CommandExecutor.quote_columns(index.columns, '"'))

        result = result.rstrip()
        print(result)

    @staticmethod
    def print_table_ddl_java(table: Table, source_db: str):
        def upper_camel_case(word: str):
            return ''.join(x.capitalize() or '_' for x in word.split('_'))

        def camel_case(word: str):
            word = upper_camel_case(word)
            return word[0].lower() + word[1:]

        result = ''

        if table.name:
            result += '/** {} */\n'.format(table.name)

        # Use Lombok annotations
        result += '@Data\n'
        result += 'public class {} implements Serializable {{\n'.format(upper_camel_case(table.code))
        result += '  private static final long serialVersionUID = 1L;\n\n'

        for c in table.columns:
            if c.name:
                result += '  /** {} */\n'.format(c.name)
            result += '  private {} {};\n'.format(TypeMapping.convert(source_db, 'java', c.data_type),
                                                  camel_case(c.code))

        result += '}'
        result = result.rstrip()
        print(result)

    def print_sequences(self, glob: str = None):
        if glob:
            try:
                pattern = re.compile(fnmatch.translate(glob), re.IGNORECASE)
            except re.error:
                print('Invalid glob: ' + glob)
                return
            sequences = [s for s in self.schema.sequences if pattern.match(s.code)]
            if len(sequences) <= 0:
                print('No matching sequences')
                return
        else:
            sequences = self.schema.sequences

        def print_sequence(s: Sequence):
            if self.horizontal_output:
                print(self.formatter.format('{:30s}', s.code))
            else:
                print('Code: {}'.format(s.code))
                print()

        def print_header():
            if self.horizontal_output:
                print_sequence(Sequence('Code'))
                print('-' * 80)

        print_header()
        for sequence in sequences:
            print_sequence(sequence)

        print('Count: {}'.format(len(sequences)))

    @staticmethod
    def print_help():
        def print_help_item(command, description):
            print('{:30s}{}'.format(command, description))

        print_help_item('COMMAND', 'DESCRIPTION')
        print('-' * 80)
        print_help_item('help', 'Print help')
        print_help_item('t', 'Toggle horizontal/vertical output. Default horizontal')
        print_help_item('tables', 'Show tables')
        print_help_item('tables PATTERN', 'Show tables matching the given shell-style glob')
        print_help_item('seq', 'Show sequences')
        print_help_item('seq PATTERN', 'Show sequences matching the given shell-style glob')
        print_help_item('table TABLE', 'Show definitions of the given table')
        print_help_item('mysql TABLE', 'Generate MySQL DDL for creating the given table')
        print_help_item('oracle TABLE', 'Generate Oracle DDL for creating the given table')
        print_help_item('java TABLE', 'Generate Java entity definition for the given table')
        print_help_item('exit, Ctrl + D', 'Exit')

    @staticmethod
    def collapse_whitespace(s) -> str:
        return CommandExecutor.whitespace_pattern.sub(' ', s)

    @staticmethod
    def quote_columns(columns: List[Column], quote: str):
        if len(columns) == 0:
            return ''
        else:
            result = '`' + '`, `'.join([c.code for c in columns]) + '`'
            return result.replace('`', quote)
