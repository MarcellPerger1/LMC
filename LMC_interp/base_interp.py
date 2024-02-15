from __future__ import annotations

import abc
from typing import TypeAlias, ClassVar

# so that it doesn't conflict with `def set(self, addr, value):`
HashSet: TypeAlias = set

MemValT: TypeAlias = int


# TODO merge the exceptions into one hierarchy
class MemoryTooSmallError(Exception):
    ...


# region extensions (TODO move to separate file)
# TODO unify with LMC_interp.errors.ExtensionDisabledError
class ExtensionDisabledError2(Exception):
    pass


# TODO str for now, should change to Enum?
ExtensionT: TypeAlias = str

# endregion


class BaseInterp(abc.ABC):
    initial_memory_value: MemValT
    supports_extensions: ClassVar[HashSet[ExtensionT]] = {}
    enabled_extensions: HashSet[ExtensionT]

    # region init
    @classmethod
    @abc.abstractmethod
    def from_memory_exact(cls, memory_exact: list[MemValT], *args, **kwargs):
        ...

    @classmethod
    def from_memory(cls, memory: list[MemValT] | None = None,
                    *args, **kwargs):
        return cls.from_memory_exact(cls._make_mem_obj(
            memory, cls._get_mem_size(memory, *args, **kwargs)),
            *args, **kwargs)

    @classmethod
    @abc.abstractmethod
    def _get_mem_size(cls, memory: list[MemValT] | None,
                          *args, **kwargs) -> int:
        ...

    @classmethod
    def _make_mem_obj(cls, memory: list[MemValT] | None,
                      mem_size: int) -> list[MemValT]:
        if memory is None:
            return [0] * mem_size
        if len(memory) > mem_size:
            raise MemoryTooSmallError("memory doesn't fit in the capacity,"
                                      " try increasing mem_size")
        extra_req = mem_size - len(memory)
        return memory + [0] * extra_req
    # endregion

    # region main/run
    @abc.abstractmethod
    def run(self):
        ...
    # endregion

    # region utils for *Instr
    @abc.abstractmethod
    def get(self, addr: int) -> int:
        ...

    @abc.abstractmethod
    def set(self, addr: int, value: MemValT):
        ...

    @property
    @abc.abstractmethod
    def acc(self) -> int:
        ...

    @acc.setter
    @abc.abstractmethod
    def acc(self, value: int):
        ...

    @abc.abstractmethod
    def jmp(self, addr: int):
        ...

    @abc.abstractmethod
    def halt(self):
        ...
    # endregion

    # region bounds checking/wrapping
    @abc.abstractmethod
    def is_addr_in_bounds(self, addr: int) -> bool:
        ...

    @abc.abstractmethod
    def normalize_addr(self, addr: int, err: Exception = None) -> int:
        ...

    @abc.abstractmethod
    def normalize_value(self, value: int) -> int:  # noexcept
        ...

    def normalize_ip(self):
        ...
    # endregion

    # region extensions
    def is_ext_enabled(self, ext: ExtensionT) -> bool:
        return ext in self.enabled_extensions

    def expect_ext_enabled(self, ext: ExtensionT, err: Exception = None):
        if self.is_ext_enabled(ext):
            return
        err = err or ExtensionDisabledError2(
            f"The {ext!r} extension is disabled.")
        raise err
    # endregion
