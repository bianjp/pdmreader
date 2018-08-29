import string
import unicodedata
import math
import itertools


# https://stackoverflow.com/a/44237289/3128576
class UnicodeFormatter(string.Formatter):
    def format_field(self, value, format_spec):
        if not isinstance(value, str) or not value or not format_spec:
            return super().format_field(value, format_spec)

        print_length = self.get_print_width(value)
        if len(value) == print_length:
            return format(value, format_spec)

        fill, align, width, format_spec = UnicodeFormatter.parse_align(format_spec)
        if width == 0:
            return value
        formatted_value = format(value, format_spec)
        pad_len = width - print_length
        if pad_len <= 0:
            return formatted_value
        left_pad = ''
        right_pad = ''
        if align in '<=':
            right_pad = fill * pad_len
        elif align == '>':
            left_pad = fill * pad_len
        elif align == '^':
            left_pad = fill * math.floor(pad_len/2)
            right_pad = fill * math.ceil(pad_len/2)
        return ''.join((left_pad, formatted_value, right_pad))

    @staticmethod
    def get_print_width(s: str):
        width = 0
        for c in s:
            # https://bugs.python.org/issue12568#msg145523
            width_type = unicodedata.east_asian_width(c)
            if width_type == 'F' or width_type == 'W':
                width += 2
            else:
                width += 1
        return width

    @staticmethod
    def parse_align(format_spec):
        format_chars = '=<>^'
        align = '<'
        fill = None
        if format_spec[1] in format_chars:
            align = format_spec[1]
            fill = format_spec[0]
            format_spec = format_spec[2:]
        elif format_spec[0] in format_chars:
            align = format_spec[0]
            format_spec = format_spec[1:]

        if align == '=':
            raise ValueError("'=' alignment not allowed in string format specifier")
        if format_spec[0] in '+- ':
            raise ValueError('Sign not allowed in string format specifier')
        if format_spec[0] == '#':
            raise ValueError('Alternate form (#) not allowed in string format specifier')
        if format_spec[0] == '0':
            if fill is None:
                fill = '0'
            format_spec = format_spec[1:]
        if fill is None:
            fill = ' '
        width_str = ''.join(itertools.takewhile(str.isdigit, format_spec))
        width_len = len(width_str)
        format_spec = format_spec[width_len:]
        if width_len > 0:
            width = int(width_str)
        else:
            width = 0
        return fill, align, width, format_spec
