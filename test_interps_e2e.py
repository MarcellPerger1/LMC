import random
import sys
import unittest
from io import StringIO
from typing import TextIO, Generic, TypeVar

from LMC_interp.interpreter_b10 import InterpreterB10
from LMC_interp.interp_b2_quick_and_dirty import InterpB2

_T = TypeVar('_T', InterpB2, InterpreterB10)


def readfile(path: str) -> str:
    with open(path, 'r') as f:
        return f.read()


class RedirectStdin:
    def __init__(self, new_stdin: TextIO):
        self.new_stdin = new_stdin

    def __enter__(self):
        self.prev_stream = sys.stdin
        sys.stdin = self.new_stdin
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        sys.stdin = self.prev_stream


class MockStdinFromString(RedirectStdin):
    def __init__(self, s: str):
        self.string = s
        self.sio = StringIO(s)  # already at start, see docs
        super().__init__(self.sio)


class MockStdoutToString:
    def __init__(self):
        self.sio = StringIO()

    @property
    def string(self):
        return self.sio.getvalue()

    def __enter__(self):
        self.prev_stream = sys.stdout
        sys.stdout = self.sio
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        sys.stdout = self.prev_stream


class CommonT(unittest.TestCase, Generic[_T]):
    ClassToTest: type[_T] = None
    # set seed + PRNG for reproducibility, use SystemRandom for
    # true random / low-budget 'fuzzing'
    rng: random.Random = random.Random(3.14)

    def test_sort_5_nums_perf(self):
        inst = self.ClassToTest.from_source(readfile('sort_5_nums_perf.lmc'))
        inst.run()
        values = [inst.get(73 + i) for i in range(5)]
        self.assertEqual(values, [-158, -56, 15, 73, 89])

    def _get_5_nums(self):
        return [self.rng.randint(-350, 350) for _ in range(5)]

    def _test_sort_5_nums_rng_once(self, source: str):
        inst: _T = self.ClassToTest.from_source(source, inp_prompt='')
        nums = self._get_5_nums()
        inp_s = '\n'.join(map(str, nums)) + '\n'
        expect_out = '\n'.join(map(str, sorted(nums))) + '\n'
        with MockStdinFromString(inp_s), MockStdoutToString() as out:
            inst.run()
        self.assertEqual(out.string, expect_out)

    def test_sort_5_nums_prng(self):
        source = readfile('sort_5_nums.lmc')
        for _ in range(50):
            self._test_sort_5_nums_rng_once(source)

    @classmethod
    def setUpClass(cls):
        if cls.ClassToTest is None:
            raise unittest.SkipTest("ClassToTest is needed for tests to run")


class TestInterpB2(CommonT[InterpB2]):
    ClassToTest = InterpB2


class TestInterpreterB10(CommonT[InterpB2]):
    ClassToTest = InterpreterB10


if __name__ == '__main__':
    unittest.main()
