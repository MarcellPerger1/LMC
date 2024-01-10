from LMC_interp.base_instruction import Instruction
from LMC_interp.data_instruction import Data


def instr_to_int_1(instr: int | Instruction | Data) -> int:
    """Convert a single Instruction/Data/int to the op in memory"""
    if isinstance(instr, Data):
        return instr.data
    if isinstance(instr, Instruction):
        return instr.get_b10_repr()
    return instr


def int_to_instr_1(op: int) -> Instruction | Data:
    """Guess what the source program might've been from the b10 codes.
    This is fairly accurate esp. if all DAT values are < 100"""
    instr = Instruction.get_instr(op)
    if not instr.is_valid():
        return Data(op)  # must be data as it wouldn't be a valid instruction
    if (canonical_forms := instr.get_canonical_forms()) is None:
        return instr  # instruction if all forms are canonical...
    if op in canonical_forms:
        return instr  # ... OR op is a canonical form
    # not a canonical form so probably data
    return Data(op)


def instructions_to_memory(instructions: list[int | Instruction | Data]):
    """Convert a list of Instruction/Data/int to the memory (list[int])"""
    return [instr_to_int_1(instr) for instr in instructions]


def memory_to_instructions(memory: list[int]) -> list[Instruction | Data]:
    """Guess what the list of Instr/Data could've been from the memory"""
    return [int_to_instr_1(op) for op in memory]
