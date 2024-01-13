import contextlib
# TODO this has been removed in 3.13, switch to setuptools._distutils
#  or something. OR just call MSVC ourselves - it can't be that hard right?
import distutils.ccompiler as ccompiler
import os
from pathlib import Path
from typing import Iterable, cast, Any

__all__ = ['compile_runtime']


class BaseCompiler:
    def __init__(self, sources: list[str], exe_path: str,
                 libraries: Iterable[str] = (), out_dir: str = None,
                 obj_dir: str = None, exe_dir: str = None,
                 out_type: str = 'executable', debug=True, verbose=False,
                 macros: Iterable[tuple[str, str | None] | tuple[str,]]=()):
        self.sources = [sources] if isinstance(sources, str) else list(sources)
        self.libraries = list(libraries)
        self.obj_dir = Path(obj_dir) if obj_dir is not None else (
            Path(out_dir) if out_dir is not None else None)
        self.exe_dir = exe_dir if exe_dir is not None else out_dir
        self.exe_name = exe_path
        self.out_type = out_type
        self.debug = debug
        self.cc = ccompiler.new_compiler()
        self.verbose = verbose
        self.macros = macros
        self.is_msvc = getattr(self.cc, 'compiler_type', None) == 'msvc'
        self.objects = None

    def compile(self):
        postargs = []
        if self.is_msvc:
            if self.debug and self.obj_dir is not None:
                postargs += ['/Fd' + str(self.obj_dir / 'vc140_fd_pdb.pdb')]
            if self.verbose:
                postargs += ['/showIncludes']
        self.objects = self.cc.compile(
            self.sources, str(self.obj_dir), debug=self.debug,
            extra_postargs=postargs,
            # typeshed bug #11271
            macros=cast(Any, list(self.macros)))

    def link(self):
        postargs = []
        if self.is_msvc:
            if self.debug and self.obj_dir is not None:
                postargs += ['/PDB:' + str(self.obj_dir / f'pdb_2_{self.exe_name}.pdb')]
            if self.verbose:
                postargs += ['/VERBOSE']
        self.cc.link(self.out_type, self.objects, self.exe_name, self.exe_dir,
                     self.libraries, debug=self.debug, extra_postargs=postargs)

    def run(self):
        self.compile()
        self.link()


class LmcRtCompiler:
    def __init__(self, sources: list[str], debug=True, verbose=False):
        self.sources = sources
        self.debug = debug
        self.verbose = verbose
        self.out_name = 'debug' if self.debug else 'release'
        self.curr_dir = Path(__file__).parent
        self.out_dir = self.curr_dir / 'out' / self.out_name
        self.base: None | BaseCompiler = None

    @contextlib.contextmanager
    def temp_cd(self, target: str | os.PathLike[str]):
        orig_cwd = os.getcwd()
        try:
            os.chdir(target)
            yield
        finally:
            os.chdir(orig_cwd)

    def run(self):
        with self.temp_cd(self.curr_dir):
            self.out_dir.mkdir(parents=True, exist_ok=True)
            self.base = BaseCompiler(
                self.sources, 'lmc_runtime.exe', [], str(self.out_dir),
                str(self.out_dir / 'objects'), debug=self.debug, verbose=self.verbose)
            self.base.run()


def compile_runtime(debug=True, verbose=False):
    LmcRtCompiler(['lmc_runtime.c'], debug, verbose).run()


if __name__ == '__main__':
    compile_runtime(verbose=True)
