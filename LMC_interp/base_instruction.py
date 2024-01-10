from __future__ import annotations

import abc
from abc import ABC
from typing import TYPE_CHECKING

from LMC_interp.errors import InvalidOpcodeError

if TYPE_CHECKING:
    from LMC_interp.interpreter_b10 import InterpreterB10 as InterpStateT


class Instruction:
    """Common base class for all LMC instructions"""

    b10_opcode_mult: int = 100  # ClassVar
    is_valid_cls: bool = True

    def is_valid(self):
        return self.is_valid_cls

    @classmethod
    def get_canonical_forms(cls) -> set[int] | None:
        """Returns the `b10op`s corresponding to the valid and useful forms of
        this instruction. None if all values of the operands would be in this set"""
        return None

    def get_b10_repr(self) -> int:
        """Returns a base 10 representation of the instruction"""
        return (self.b10_opcode_mult * self.get_b10_opcode()
                + self.get_b10_operands())

    @classmethod
    # protected
    def from_b10_int(cls, op: int) -> Instruction:
        return cls.from_b10_opcode_operand(op // 100, op % 100)

    @classmethod
    def from_b10_operand(cls, operand: int) -> Instruction:
        """Might not always work properly"""
        return cls.from_b10_opcode_operand(cls.get_b10_opcode(), operand)

    @classmethod
    def from_default_operand(cls) -> Instruction | None:
        """Returns the default version of this function. None if no default.
        You could consider this the default ctor, but this doesn't
        force anything on the __init__ of the subclass.
        Examples:
        >>> from LMC_interp.instructions import AddInstr, HaltInstr, InputInstr
        >>> HaltInstr.from_default_operand() == HaltInstr(0)
        True
        >>> AddInstr.from_default_operand() is None
        True
        >>> InputInstr.from_default_operand() == InputInstr()
        True"""
        return None

    # protected
    @classmethod
    @abc.abstractmethod
    def from_b10_opcode_operand(cls, opcode: int, operand: int) -> Instruction:
        # Don't want to force classes to use __init__ in a specific way
        # so make it a special classmethod
        ...

    @abc.abstractmethod
    def run(self, interp: InterpStateT):
        """Run this instruction"""

    @classmethod
    @abc.abstractmethod
    def get_b10_opcode(cls) -> int:
        """Return the denary opcode associated with this class"""

    @abc.abstractmethod
    def get_b10_operands(self) -> int:
        """Return base 10 representation of the operand(s)"""

    # <NOT FOR OVERLOADING> {
    @classmethod
    def get_instr_cls(cls, op: int):
        opcode = op // 100
        return INSTR_DISPATCH.get(opcode, InvalidInstr)

    @classmethod
    def get_instr(cls, op: int) -> Instruction:
        return cls.get_instr_cls(op).from_b10_int(op)
    # } </NOT FOR OVERLOADING>


class InstrSingleOpcodeCommon(Instruction, ABC):
    opcode: int  # abstract

    def __init__(self, operand: int):
        self.operand = operand

    def __eq__(self, other: Instruction | InstrSingleOpcodeCommon):
        # Class lower down in the hierarchy should decide equality
        if isinstance(self, type(other)):
            # Other --> xyz --> Self => Self decides
            return self.operand == other.operand and self.opcode == other.opcode
        if isinstance(other, type(self)):
            # Self --> xyz --> Other => Other decides
            # (perhaps inherits this same method)
            return NotImplemented
        # fallback - if district classes and both inherit from this,
        #  just check opcode and operand.
        # Later, this could check the first common class in MRO,
        #  then use its equality function?
        if isinstance(other, InstrSingleOpcodeCommon):
            return self.operand == other.operand and self.opcode == other.opcode
        return NotImplemented

    @classmethod
    def from_b10_opcode_operand(cls, opcode: int, operand: int) -> Instruction:
        return cls(operand)

    @classmethod
    def get_b10_opcode(cls) -> int:
        return cls.opcode

    def get_b10_operands(self) -> int:
        return self.operand


# not meant to be @register()d but returned from dispatch routines in e.g. 9xx
class InstrFixedOperand(Instruction, ABC):
    opcode: int  # abstract
    operand: int  # abstract

    def __init__(self): pass

    def __eq__(self, other: InstrFixedOperand | Instruction):
        if not isinstance(other, InstrFixedOperand):
            return NotImplemented
        return (type(self) == type(other) and self.operand == other.operand
                and self.opcode == other.opcode)

    @classmethod
    def from_default_operand(cls) -> Instruction | None:
        return cls()

    @classmethod
    def from_b10_opcode_operand(cls, opcode: int, operand: int) -> Instruction:
        return cls()

    @classmethod
    def get_b10_opcode(cls) -> int:
        return cls.opcode

    def get_b10_operands(self) -> int:
        return self.operand


INSTR_DISPATCH: dict[int, type[Instruction]] = {}


def _register_instr(cls: type[Instruction], opcode: int = None):
    b10_opcode = opcode if opcode is not None else cls.get_b10_opcode()
    INSTR_DISPATCH[b10_opcode] = cls
    return cls


def register_instr(cls_or_opcode: type[Instruction] | int = None, opcode: int = None):
    match (cls_or_opcode, opcode):
        case (None, None):  # @register_instr()
            return lambda cls_: _register_instr(cls_)
        case (None, opcode):  # @register_instr(opcode=6)
            return lambda cls_: _register_instr(cls_, opcode)
        case (type() as cls, None):  # @register_instr
            return _register_instr(cls)
        case (opcode, None):  # @register_instr(6)
            return lambda cls_: _register_instr(cls_, opcode)
        case (cls, opcode):  # register_instr(cls, 6), register_instr(cls, opcode=6)
            return _register_instr(cls, opcode)
        case _: assert 0, "should be unreachable"


class InvalidInstr(Instruction):
    is_valid_cls = False

    def __init__(self, opcode: int, operand: int):
        self.opcode = opcode
        self.operand = operand

    @classmethod
    def from_b10_opcode_operand(cls, opcode: int, operand: int):
        return cls(opcode, operand)

    def run(self, interp_state: InterpStateT):
        opcode = self.opcode
        raise InvalidOpcodeError(f"Invalid instruction ({opcode=})")

    # this dark magic is to not violate LSP while
    # trying to give more useful information if an instance is available
    def get_b10_opcode(self=None) -> int:
        if self is not None and isinstance(self, InvalidInstr):
            return self.opcode
        return -1  # return something that should always be invalid

    def get_b10_operands(self) -> int:
        return self.operand
