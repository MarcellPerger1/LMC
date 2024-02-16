try:
    # noinspection PyProtectedMember,PyCompatibility
    from distutils._msvccompiler import MSVCCompiler
except ImportError:
    # noinspection PyUnresolvedReferences,PyProtectedMember
    from setuptools._distutils._msvccompiler import MSVCCompiler

# noinspection PyUnresolvedReferences
__all__ = ['MSVCCompiler']
