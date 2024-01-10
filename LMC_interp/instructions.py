from __future__ import annotations

import abc
from typing import TYPE_CHECKING

from LMC_interp.base_instruction import (
    Instruction, register_instr, InstrSingleOpcodeCommon, InstrFixedOperand)
from LMC_interp.errors import InvalidOperandError

if TYPE_CHECKING:
    from LMC_interp.interpreter_b10 import InterpreterB10 as InterpStateT


@register_instr()
class HaltInstr(InstrSingleOpcodeCommon):
    opcode = 0

    def __init__(self, operand: int = 0):
        # still store unused operand but give it default for ease of use
        super().__init__(operand)

    @classmethod
    def get_canonical_forms(cls) -> set[int] | None:
        return {cls().get_b10_repr()}

    @classmethod
    def from_default_operand(cls) -> Instruction | None:
        return HaltInstr()

    def run(self, interp: InterpStateT):
        interp.is_halted = True


@register_instr()
class AddInstr(InstrSingleOpcodeCommon):
    opcode = 1

    def run(self, interp: InterpStateT):
        interp.acc += interp.get(self.operand)


@register_instr()
class SubInstr(InstrSingleOpcodeCommon):
    opcode = 2

    def run(self, interp: InterpStateT):
        interp.acc -= interp.get(self.operand)


@register_instr()
class StoreInstr(InstrSingleOpcodeCommon):
    opcode = 3

    def run(self, interp: InterpStateT):
        interp.set(self.operand, interp.acc)


@register_instr()
class LoadInstr(InstrSingleOpcodeCommon):
    opcode = 5

    def run(self, interp: InterpStateT):
        interp.acc = interp.get(self.operand)


@register_instr()
class BranchInstr(InstrSingleOpcodeCommon):
    opcode = 6

    def run(self, interp: InterpStateT):
        interp.jmp(self.operand)


@register_instr()
class BranchZeroInstr(InstrSingleOpcodeCommon):
    opcode = 7

    def run(self, interp: InterpStateT):
        if interp.acc == 0:
            interp.jmp(self.operand)


@register_instr()
class BranchPosInstr(InstrSingleOpcodeCommon):
    opcode = 8

    def run(self, interp: InterpStateT):
        # in LMC, 0 counts as positive - weird
        if interp.acc >= 0:
            interp.jmp(self.operand)


@register_instr()
class IOInstr(InstrSingleOpcodeCommon):
    opcode = 9

    def is_valid(self):
        return self.dispatch_operand().is_valid_cls

    @classmethod
    def get_canonical_forms(cls) -> set[int] | None:
        return {cls(operand).get_b10_repr() for operand in (1, 2, 22)}

    def dispatch_operand(self) -> Instruction:
        match self.operand:
            case 1:
                return InputInstr()
            case 2:
                return OutputInstr()
            case 22:
                return OutputCharInstr()
            case operand:
                return InvalidIOInstr(operand)

    def run(self, interp: InterpStateT):
        self.dispatch_operand().run(interp)


class BaseIOSubInstr(abc.ABC):
    opcode = 9

    @abc.abstractmethod
    def to_io_instr(self) -> IOInstr:
        ...


class FixedOperandIOSubInstr(BaseIOSubInstr, InstrFixedOperand, abc.ABC):
    opcode = 9
    operand: int  # abstract

    def to_io_instr(self) -> IOInstr:
        return IOInstr(self.operand)


class InvalidIOInstr(InstrSingleOpcodeCommon, BaseIOSubInstr):
    opcode = 9
    is_valid_cls = False

    def to_io_instr(self) -> IOInstr:
        return IOInstr(self.operand)

    def run(self, interp: InterpStateT):
        raise InvalidOperandError("Invalid operand for opcode 9xx (INP/OUT/OTC)")


class InputInstr(FixedOperandIOSubInstr):
    opcode = 9
    operand = 1

    def run(self, interp: InterpStateT):
        interp.acc = interp.io.read_num()


class OutputInstr(FixedOperandIOSubInstr):
    opcode = 9
    operand = 2

    def run(self, interp: InterpStateT):
        interp.io.write_num(interp.acc)


class OutputCharInstr(FixedOperandIOSubInstr):
    opcode = 9
    operand = 22

    def run(self, interp: InterpStateT):
        interp.ext_otc__expect_enabled()
        interp.io.write_char(interp.acc)


def ensure_instr_registered():
    """This function exists purely so that this file is imported
    and the @register_instr() side effects are run"""
