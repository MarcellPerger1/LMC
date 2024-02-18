from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from LMC_interp.interpreter_b10 import InterpreterB10


# noinspection PyMethodMayBeStatic
class IOMgr:
    def __init__(self, interp: InterpreterB10):
        self.interp = interp  # just for the config (e.g. value_range)
        self.is_line_mode = False

    def write_num(self, num: int):
        print(num, end='' if self.is_line_mode else '\n')

    def write_char(self, ascii_value: int):
        # This function starts a 'line' if not already started and
        #  everything will be output onto that single line without any spaces
        #  until \n is output to end the line
        #  (e.g. OTC 'a'; OUT 1; OUT 2; prints 'a12' NOT 'a\n 1\n 2\n').
        # After the line is finished, outputting numbers goes back
        #  to the usual behavior of 1 number / line; outputting a char will
        #  put it back into the 'line' mode.
        # This is so that code not using OTC gets the expected behavior
        #  while allowing easier mixing of text and numbers on a single line
        #  and (as long as all 'line'-s are terminated), using OTC in one part
        #  of the program doesn't impact printing done by another part of the program
        # So this way it's both backwards-compatible and easier to mix the two
        char = chr(ascii_value)
        print(char, end='')
        if char == '\n':
            self.is_line_mode = False
        else:
            self.is_line_mode = True

    def read_num(self) -> int:
        num_range = self.interp.value_range
        while True:
            try:
                value = int(input(self.interp.inp_prompt))
            except ValueError:
                print('Input must be an integer')
                continue
            if not self.interp.wrap_values:
                return value  # allow any value if no wrap_values
            if num_range[0] <= value <= num_range[1]:
                return value
            else:
                print('Input out of range')
