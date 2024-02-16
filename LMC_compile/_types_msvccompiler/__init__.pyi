from typing import ClassVar, Literal, TypeAlias

try:
    from distutils.ccompiler import CCompiler
except ImportError:
    # noinspection PyProtectedMember
    from setuptools._distutils.ccompiler import CCompiler

__all__ = ['MSVCCompiler']

_PlatName: TypeAlias = Literal['win32', 'win-amd64', 'win-arm32', 'win-arm64']

class MSVCCompiler(CCompiler):
    compiler_type: str = 'msvc'
    src_extensions: ClassVar[list[str]] = [
        '.c', '.cc', '.cpp', '.cxx', '.rc', '.mc']
    obj_extension: ClassVar[str] = '.obj'
    res_extension: ClassVar[str] = '.obj'
    static_lib_extension: ClassVar[str] = '.lib'
    shared_lib_extension: ClassVar[str] = '.dll'
    static_lib_format: ClassVar[str] = '%s%s'
    shared_lib_format: ClassVar[str] = '%s%s'
    exe_extension: ClassVar[str] = '.exe'

    compile_options: list[str]
    compile_options_debug: list[str]
    ldflags_exe: list[str]
    ldflags_exe_debug: list[str]
    ldflags_shared: list[str]
    ldflags_shared_debug: list[str]
    ldflags_static: list[str]
    ldflags_static_debug: list[str]

    def initialize(self, plat_name: _PlatName | None = None):
        ...