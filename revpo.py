"""
RevPo
Evaluator and REPL for reverse Polish (aka postfix) notation expressions.
"""
import sys
import unittest
from operator import add, sub, mul, truediv, pow
from typing import Any, List, Optional, Union


class TooManyOperands(ValueError):
    "Too many operands were provided"


class InsufficientOperands(ValueError):
    "There aren't enough operands to evaluate the expression"


class UnsupportedOperator(ValueError):
    "An unsupported operator was used"


string_to_operator_map = {
    '+': add,
    '-': sub,
    '*': mul,
    '/': truediv,
    '**': pow,
}


def _tokenize(string: str) -> List[str]:
    """
    In: '4 2 ** 1 +'
    Out: ['4', '2', '**', '1', '+']
    """
    tokens = string.split()

    return tokens


def _atomize(token: str):
    """
    Transform token into atom (int, float, or function) and return it,
    or raise an exception.
    """
    try:
        atom = int(token)
    except ValueError:
        try:
            atom = float(token)
        except ValueError:
            try:
                atom = string_to_operator_map[token]
            except KeyError:
                raise UnsupportedOperator(f'Unsupported operator "{token}"')

    return atom


def _parse(tokens: List[str]) -> List[Any]:
    """
    In: ['4', '2', '**', '1', '+']
    Out: [4, 2, <built-in function pow>, 1, <built-in function add>]
    """
    atoms = [_atomize(token) for token in tokens]

    return atoms


class OperandStack:
    """
    Handles a stack of operands and operations on said stack.
    Used to transform an expression (whether that means transforming
    it into a different kind of expression or evaluating it).
    """
    builder_functions = {
        None: lambda op, left, right: op(left, right),
        'to_infix': lambda op, left, right: f'({left} {op} {right})',
        'to_prefix': lambda op, left, right: f'({op} {left} {right})',
    }

    def __init__(self, transform=None):
        self.stack = []
        self.transform = transform
        self.build_operand = self.builder_functions[transform]

    def append_operand(self, operand):
        self.stack.append(operand)

    def apply_operator(self, operator):
        try:
            second_operand = self.stack.pop()
            first_operand = self.stack.pop()
        except IndexError:
            raise InsufficientOperands('Insufficient operands')

        operand = self.build_operand(operator, first_operand, second_operand)
        self.stack.append(operand)

    def get_result(self) -> Union[int, float, str]:
        if len(self.stack) != 1:
            raise TooManyOperands('Too many operands')

        if not self.transform:
            return self.stack.pop()

        return self.stack.pop()[1:-1]


def eval(string: str, transform: Optional[str]=None) -> Union[int, float, str]:
    """
    Evaluate a reverse Polish notation expression and return its result.

    In: '4 2 ** 1 +'
    Out: 17

    In: '4 2 ** 1 +', transform='to_infix'
    Out: '(4 ** 2) + 1'

    In: '4 2 ** 1 +', transform='to_prefix'
    Out: '+ (** 4 2) 1'
    """
    if not transform:
        elements = _parse(_tokenize(string))
        is_operator = callable
    else:
        elements = _tokenize(string)
        is_operator = lambda s: s in string_to_operator_map

    stack = OperandStack(transform=transform)

    for element in elements:
        if is_operator(element):
            stack.apply_operator(element)
        else:
            stack.append_operand(element)

    return stack.get_result()


def repl() -> None:
    """
    Evaluate reverse Polish notation expressions in a read-eval-print loop.
    """
    while True:
        input_string = input('RevPo (type q to quit)> ')

        if input_string == 'q':
            return

        command = input_string.split()[0]
        if command in ('in', 'pre'):
            input_string = ' '.join(input_string.split()[1:])
            if command == 'in':
                transform = 'to_infix'
            else:
                transform = 'to_prefix'
        else:
            transform = None

        try:
            print(eval(input_string, transform=transform))
        except Exception as e:
            print('Error:', e)


class RevPoTests(unittest.TestCase):
    def test_postfix_notation_eval(self):
        ints = '5 1 2 + 4 * + 3 -'
        floats = '1 2 + 4 * 5 + 4.5 -'
        division = '4 2 / 1 - 4 +'
        exponentiation = '4 2 ** 1 +'
        negative_numbers = '-7 -7 *'

        self.assertEqual(eval(ints), 14)
        self.assertEqual(eval(floats), 12.5)
        self.assertEqual(eval(division), 5)
        self.assertEqual(eval(exponentiation), 17)
        self.assertEqual(eval(negative_numbers), 49)

    def test_unusual_input_eval(self):
        extra_spaces = '  4    2  + '
        too_many_operands = '5 4 1 +'
        insufficient_operands = '7 *'
        unsupported_operator = '7 7 &'
        weird_token = '3b'

        self.assertEqual(eval(extra_spaces), 6)
        with self.assertRaises(TooManyOperands):
            eval(too_many_operands)
        with self.assertRaises(InsufficientOperands):
            eval(insufficient_operands)
        with self.assertRaises(UnsupportedOperator):
            eval(unsupported_operator)
        with self.assertRaises(UnsupportedOperator):
            eval(weird_token)

    def test_transform_eval(self):
        postfix = '5 1 2 + 4 * + 3 -'
        infix = '(5 + ((1 + 2) * 4)) - 3'
        prefix = '- (+ 5 (* (+ 1 2) 4)) 3'

        self.assertEqual(eval(postfix, transform='to_infix'), infix)
        self.assertEqual(eval(postfix, transform='to_prefix'), prefix)


if __name__ == '__main__':
    if sys.argv[-1] == 'tests':
        sys.argv.pop()
        unittest.main()
    else:
        repl()
