class TypeUtil:
    numeric_types = ('number', 'numeric', 'float', 'double', 'integer', 'int', 'real', 'decimal')
    string_types = ('char', 'text', 'clob')

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
