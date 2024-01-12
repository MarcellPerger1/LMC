import time

from LMC_interp.interpreter_b10 import InterpreterB10
from LMC_interp.parse_asm import AsmParser


def readfile(path: str):
    with open(path) as f:
        return f.read()


class PerfSort5:
    PATH = 'sort_5_nums_perf.lmc'

    def __init__(self):
        self.read_times = []
        self.parse_times = []
        self.run_times = []
        self.total_times = []

    def _update_stats(self, t0: float, t1: float, t2: float, t3: float):
        self.read_times.append(t1 - t0)
        self.parse_times.append(t2 - t1)
        self.run_times.append(t3 - t2)
        self.total_times.append(t3 - t0)

    def run_once(self):
        t0 = time.perf_counter()
        src = readfile(self.PATH)
        t1 = time.perf_counter()
        ip = InterpreterB10.from_source(src)
        t2 = time.perf_counter()
        ip.run()
        t3 = time.perf_counter()
        # only assign times at end to not interfere with perf
        self._update_stats(t0, t1, t2, t3)

    def run(self, n=1_000):
        for i in range(n):
            self.run_once()
        self.print_stats()

    @classmethod
    def get_min_avg(cls, dataset: list[float]):
        return min(dataset), sum(dataset)/(len(dataset) or 1)

    @classmethod
    def fmt_min_avg(cls, dataset: list[float]) -> str:
        d_min, d_avg = cls.get_min_avg(dataset)
        return f"min={d_min * 1000:>7.3f}ms, avg={d_avg * 1000:>7.3f}ms"

    def print_stats(self):
        print(f'Read file:  {self.fmt_min_avg(self.read_times)}')
        print(f'Parse code: {self.fmt_min_avg(self.parse_times)}')
        print(f'Run code:   {self.fmt_min_avg(self.run_times)}')
        print(f'Total time: {self.fmt_min_avg(self.total_times)}')
        parsed = AsmParser(readfile(self.PATH)).parse()
        print(f'Instructions in file: {len(parsed.instructions):>5}')
        ip = InterpreterB10(parsed.memory)
        ip.run()
        print(f'Instructions ran:     {ip.n_instr:>5}')


def main():
    PerfSort5().run()


if __name__ == '__main__':
    main()
