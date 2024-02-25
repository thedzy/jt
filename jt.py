import argparse
import json
import sys

from pathlib import Path


def main():
    settings = dict(style=options.style, quote=options.quote, equals=options.equals,
                    key_colour=options.key_colour, key_bold=options.key_bold, key_inverted=options.key_inverted,
                    value_colour=options.value_colour, value_bold=options.value_bold,
                    value_inverted=options.value_inverted,
                    other_colour=options.other_colour, other_bold=options.other_bold,
                    other_inverted=options.other_inverted,
                    printer=print, width=options.width, display_type=options.display_type)

    # Parse and print
    parsed_datas: list = []
    """if not sys.stdin.isatty():
        try:
            input_data: str = sys.stdin.read()
            json_data: dict = json.loads(input_data)
            parsed_datas.append(json_data)
        except json.decoder.JSONDecodeError as err:
            display_json_err(err)"""

    for content in options.contents:
        if Path(content).is_file():
            with open(content, 'r') as json_file:
                try:
                    file_contents: str = json_file.read()
                    parsed_datas.append(json.loads(file_contents))
                except json.decoder.JSONDecodeError as err:
                    display_json_err(err)
                except FileNotFoundError as err:
                    print(f'The file "{content}" was not found.', file=sys.stderr)
                except PermissionError as err:
                    print(f'You do not have permission to read the file "{content}".', file=sys.stderr)
                except UnicodeDecodeError as err:
                    print(f'The file "{content}" encoding is not supported.', file=sys.stderr)
                except Exception as err:
                    print(f'An unexpected error occurred while reading "{content}": {err}', file=sys.stderr)
        else:
            try:
                parsed_datas.append(json.loads(content))
            except json.decoder.JSONDecodeError as err:
                display_json_err(err)

    # print parsed data
    for parsed_data in parsed_datas:
        print_tree(parsed_data, **settings)


def display_json_err(err: json.decoder.JSONDecodeError) -> None:
    """
    Print posistion of the error, both line and column
    :param err: Exception
    :return: None
    """
    print('JSON parsing error:', f'{err.msg}: line {err.lineno} column {err.colno} (char {err.pos})', file=sys.stderr)
    lines: list = err.doc.splitlines()
    print('\n'.join(lines[0:err.lineno]), file=sys.stderr)
    print('-' * (err.colno - 1) + '^', file=sys.stderr)


def print_tree(dict_obj: dict, indent: str = '', style: int = 0, null: str = None,
               quote: str = '\'', equals='=',
               key_colour: str = 'blue', key_bold: bool = True, key_inverted: bool = False,
               value_colour: str = 'green', value_bold: bool = True, value_inverted: bool = False,
               other_colour: str = 'white', other_bold: bool = False, other_inverted: bool = False,
               printer: callable = print, width: int = 1, display_type: bool = False
               ) -> None:
    """
    Pretty print a dictionary as a tree (recursive)
    :param dict_obj: (dict) Object to parse
    :param indent: (int) Indent level
    :param style: (list) Hide value if value does not match pattern
    :param null: String to display for null values
    :param quote: String to display for quotes
    :param equals: String used for the equals or relation
    :param key_colour: Name of colour od escape sequence
    :param key_bold: Use bold colours
    :param key_inverted: Use inverted colours
    :param value_colour: Name of colour od escape sequence
    :param value_bold: Use bold colours
    :param value_inverted: Use inverted colours
    :param other_colour: Name of colour od escape sequence
    :param other_bold: Use bold colours
    :param other_inverted: Use inverted colours
    :param printer: Function to use for printing (ex logger.info)
    :param width: The indent width
    :param display_type: Display the value type with the value
    :return: None
    """
    kwargs = {
        'style': style,
        'null': null,
        'key_colour': key_colour,
        'key_bold': key_bold,
        'key_inverted': key_inverted,
        'quote': quote,
        'equals': equals,
        'value_colour': value_colour,
        'value_bold': value_bold,
        'value_inverted': value_inverted,
        'other_colour': other_colour,
        'other_bold': other_bold,
        'other_inverted': other_inverted,
        'printer': printer,
        'width': width,
        'display_type': display_type
    }

    def get_style(s):
        symbols_sets = [
            ("├─", "└─", "│ ", "  ", "─", "┐ ", "┘"),  # 0
            ("┠─", "┖─", "┃ ", "  ", "─", "┒ ", "┘"),  # 1
            ("┣━", "┗━", "┃ ", "  ", "━", "┓ ", "┛"),  # 2
            ("╟─", "╙─", "║ ", "  ", "─", "╖ ", "┘"),  # 3
            ("╠═", "╚═", "║ ", "  ", "═", "╗ ", "╝"),  # 4
            ("├─", "╰─", "│ ", "  ", "─", "╮ ", "╯"),  # 5
            ("╏╺", "┗╺", "╏ ", "  ", "╺", "┓ ", "╸╸╸╸"),  # 6
            ("┡━", "┗━", "│ ", "  ", "━", "┒ ", "╾╶╶"),  # 7
            ("┣━", "┺━", "┃ ", "  ", "━", "╅╴", "╾╶╶"),  # 8
            ("▙▄", "▙▄", "▌ ", "  ", "▄", "▖ ", "▊▋▌▍▎▏"),  # 9
            ("▕╲", " ╲", "▕ ", "  ", "▁", "▁ ", "╳╳╳╳╲"),  # 10

        ]
        if s >= len(symbols_sets):
            s = 0

        inset = ' ' * width if len(indent) > 0 else ''

        return {
            'start': symbols_sets[s][5],
            'mid': inset + symbols_sets[s][0],
            'end': inset + symbols_sets[s][1],
            'cont': inset + symbols_sets[s][2],
            'none': inset + symbols_sets[s][3],
            'unnamed': symbols_sets[s][4] * width + symbols_sets[s][5],
            'null': symbols_sets[s][6]
        }

    null = get_style(style)['null'] if null is None else null

    # get colour
    def get_colour(colour='none', bold=False, inverted=False):
        """
        Get the colour is specified by name
        :param colour:
        :param bold:
        :param inverted:
        :return:
        """
        if key_colour == value_colour == other_colour == 'none':
            return ''
        colours = dict(
            black='\x1B[30m',
            red='\x1B[31m',
            green='\x1B[32m',
            yellow='\x1B[33m',
            blue='\x1B[34m',
            magenta='\x1B[35m',
            cyan='\x1B[36m',
            white='\x1B[37m',
            none='\x1B[0m'
        )
        if colour in colours:
            temp_colour = colours['none']
            temp_colour += colours[colour]
            if bold:
                temp_colour += "\x1B[1m"
            if inverted:
                temp_colour += "\x1B[7m"
            # temp_colour += colours['none']
        else:
            return colour

        return temp_colour

    if len(indent) == 0:
        printer(f'{get_colour(other_colour, other_bold, other_inverted)}{get_style(style)["start"]}{get_colour()}')

    # Get indent symbols
    def symbol(i, l):
        return f'{get_colour(other_colour, other_bold, other_inverted)}{get_style(style)["mid"] if i + 1 != l else get_style(style)["end"]}{get_colour()}'

    def next_symbol(i, l):
        return f'{get_colour(other_colour, other_bold, other_inverted)}{get_style(style)["cont"] if i + 1 != l else get_style(style)["none"]}{get_colour()}'

    # Format keys
    def format_key(k):
        if isinstance(k, str) and quote:
            return f'{get_colour(key_colour, key_bold, key_inverted)}{quote}{k}{quote}{get_colour()}'
        else:
            return f'{get_colour(key_colour, key_bold, key_inverted)}{k}{get_colour()}'

    def format_value(v):
        instance_type = f'({type(v).__name__})' if display_type else ''
        if isinstance(v, str):
            return f'{get_colour(value_colour, value_bold, value_inverted)}{quote}{v}{quote} {instance_type}{get_colour()}'
        else:
            return f'{get_colour(value_colour, value_bold, value_inverted)}{v} {instance_type}{get_colour()}'

    def format_type(t):
        instance_type = f'({type(t).__name__})' if display_type else ''
        return f'{get_colour(value_colour, value_bold, value_inverted)}{instance_type}{get_colour()}'

    def format_other(o):
        return f'{get_colour(other_colour, other_bold)}{o}{get_colour()}'

    # Draw keys and values
    length = len(dict_obj)
    if isinstance(dict_obj, dict):
        if length == 0:
            printer(f'{indent}{symbol(0, 1)}{format_other(null)}')
        for index, key_value in enumerate(dict_obj.items()):
            key, value = key_value
            if isinstance(dict_obj[key], dict):
                printer(f'{indent}{symbol(index, length)} {format_key(key)}')
                print_tree(dict_obj[key], indent + next_symbol(index, length), **kwargs)
            elif isinstance(dict_obj[key], (list, tuple, set, frozenset)):
                printer(f'{indent}{symbol(index, length)} {format_key(key)}')
                print_tree(dict_obj[key], indent + next_symbol(index, length), **kwargs)
            else:
                printer(
                    f'{indent}{symbol(index, length)} {format_key(key)} {format_other(equals)} {format_value(value)}')
    if isinstance(dict_obj, (list, tuple, set, frozenset)):
        if length == 0:
            printer(f'{indent}{symbol(0, 1)}{format_other(null)}')
        for index, value in enumerate(dict_obj):
            if isinstance(value, dict):
                printer(
                    f'{indent}{symbol(index, length)}{format_other(get_style(style)["unnamed"])} {format_type(dict_obj)}')
                print_tree(value, indent + next_symbol(index, length), **kwargs)
            elif isinstance(value, (list, tuple, set, frozenset)):
                printer(
                    f'{indent}{symbol(index, length)}{format_other(get_style(style)["unnamed"])} {format_type(dict_obj)}')
                print_tree(value, indent + next_symbol(index, length), **kwargs)
            else:
                printer(f'{indent}{symbol(index, length)} {format_value(value)}')


if __name__ == '__main__':
    # Create argument parser
    parser = argparse.ArgumentParser(description='Print json tree')

    # Colour parameter options
    colours = [
        'black',
        'red',
        'green',
        'yellow',
        'blue',
        'magenta',
        'cyan',
        'white',
        'none',
    ]

    general_style = parser.add_argument_group('General style')
    general_style.add_argument('--style', type=int, default=0,
                               action='store', dest='style',
                               help=' default=%(default)s')
    general_style.add_argument('--null-char', type=str, default=None,
                               action='store', dest='null',
                               help='default=%(default)s')
    general_style.add_argument('--quote', type=str, default='"',
                               action='store', dest='quote',
                               help='default="%(default)s"')
    general_style.add_argument('--equals', type=str, default='"',
                               action='store', dest='equals',
                               help='default="%(default)s"')
    general_style.add_argument('--width', type=int, default=0,
                               action='store', dest='width',
                               help='default=%(default)s')

    key_style = parser.add_argument_group('Key style')
    key_style.add_argument('--key-colour', type=str, default='none', choices=colours,
                           action='store', dest='key_colour',
                           help='default=%(default)s')
    key_bold = key_style.add_mutually_exclusive_group()
    key_bold.add_argument('--no-key-bold', default=False,
                          action='store_false', dest='key_bold',
                          help='default')
    key_bold.add_argument('--key-bold', default=False,
                          action='store_true', dest='key_bold',
                          help='')
    key_style.add_argument('--key-inverted', default=False,
                           action='store_true', dest='key_inverted',
                           help='default=%(default)s')

    value_style = parser.add_argument_group('Value style')
    value_style.add_argument('--value-colour', type=str, default='none', choices=colours,
                             action='store', dest='value_colour',
                             help='default=%(default)s')
    value_bold = value_style.add_mutually_exclusive_group()
    value_bold.add_argument('--no-value-bold', default=False,
                            action='store_false', dest='value_bold',
                            help='default')
    value_bold.add_argument('--value-bold', default=False,
                            action='store_true', dest='value_bold',
                            help='')
    value_style.add_argument('--value-inverted', default=False,
                             action='store_true', dest='value_inverted',
                             help='default=%(default)s')

    other_style = parser.add_argument_group('Other style')
    other_style.add_argument('--other-colour', type=str, default='none', choices=colours,
                             action='store', dest='other_colour',
                             help='default=%(default)s')
    other_bold = other_style.add_mutually_exclusive_group()
    other_bold.add_argument('--no-other-bold', default=True,
                            action='store_false', dest='other_bold',
                            help='default')
    other_bold.add_argument('--other-bold', default=True,
                            action='store_true', dest='other_bold',
                            help='')
    other_style.add_argument('--other-inverted', default=False,
                             action='store_true', dest='other_inverted',
                             help='default=%(default)s')

    parser.add_argument('--display-type', default=False,
                        action='store_true', dest='display_type',
                        help='default=%(default)s')

    parser.add_argument(default=[], nargs=argparse.ZERO_OR_MORE,
                        action='store', dest='contents',
                        help='file/json string')

    options = parser.parse_args()

    main()
