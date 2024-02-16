import contextlib
import sys
from pathlib import Path
from typing import Iterable, cast, Any

try:
    import distutils.ccompiler as ccompiler
except ImportError:
    # noinspection PyProtectedMember
    import setuptools._distutils.ccompiler as ccompiler
from LMC_compile._types_msvccompiler import MSVCCompiler

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
            assert isinstance(self.cc, MSVCCompiler)
            try:  # using internal methods here so use try/catch
                self.cc.initialize()
                self.cc.compile_options_debug.remove('/W3')
                self.cc.compile_options.remove('/W3')
            except (TypeError, AttributeError, ValueError):
                pass
            postargs += ['/std:c17', '/W4']
            if self.debug and self.obj_dir is not None:
                postargs += ['/Fd' + str(self.obj_dir / 'vc140_fd_pdb.pdb')]
            if self.verbose:
                postargs += ['/showIncludes']
            else:
                postargs += ['/nologo']
        self.objects = self.cc.compile(
            self.sources, str(self.obj_dir), debug=self.debug,
            extra_postargs=postargs,
            # typeshed bug #11271
            macros=cast(Any, list(self.macros)))

    def link(self):
        postargs = []
        if self.is_msvc:
            if self.debug:
                if self.obj_dir is not None:
                    postargs += ['/PDB:' + str(self.obj_dir / f'pdb_2_{self.exe_name}.pdb')]
                postargs += ['/LTCG:OFF']
            if self.verbose:
                postargs += ['/VERBOSE']
            else:
                postargs += ['/NOLOGO']
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

    def run(self):
        with contextlib.chdir(self.curr_dir):
            self.out_dir.mkdir(parents=True, exist_ok=True)
            self.base = BaseCompiler(
                self.sources, 'lmc_runtime.exe', [], str(self.out_dir),
                str(self.out_dir / 'objects'), debug=self.debug, verbose=self.verbose)
            self.base.run()


def compile_runtime(debug=True, verbose=False):
    LmcRtCompiler(['lmc_runtime.c'], debug, verbose).run()


def main(argv: list[str] = None):
    if argv is None:
        argv = sys.argv[1:]
    import argparse
    p = argparse.ArgumentParser('python -m LMC_compile.compile')
    debug_group = p.add_mutually_exclusive_group()
    debug_group.add_argument('-O', '--optimize',
                             action='store_false', help='Compile with optimizations',
                             dest='debug', default=True)
    debug_group.add_argument('-d', '--debug', '--no-optimize',
                             action='store_true', dest='debug',
                             help='Disable optimisations')
    p.add_argument('-v', '--verbose', action='store_true',
                   help="Be VERY verbose")
    args = p.parse_args(argv)
    compile_runtime(args.debug, args.verbose)


if __name__ == '__main__':
    main()
