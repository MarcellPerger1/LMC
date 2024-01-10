from __future__ import annotations

from dataclasses import dataclass, field

from LMC_interp.base_instruction import Instruction
from LMC_interp.data_instruction import Data
from LMC_interp.errors import LMCError, ExtensionDisabledError
from LMC_interp.instruction_conv import instructions_to_memory
from LMC_interp.instructions import (
    HaltInstr, AddInstr, SubInstr, StoreInstr, LoadInstr,
    BranchInstr, BranchZeroInstr, BranchPosInstr,
    InputInstr, OutputInstr, OutputCharInstr)


@dataclass
class ParsedInstr:
    opcode: str
    operand: str | int | None = None
    labels: set[str] = field(default_factory=set)


class AsmParseError(LMCError):
    pass


class AsmUnknownLabelError(AsmParseError):
    pass


NAME_TO_CLS_MAP: dict[str, type[Instruction]] = {
    'HLT': HaltInstr,
    'ADD': AddInstr,
    'SUB': SubInstr,
    'STA': StoreInstr,
    'STO': StoreInstr,
    'LDA': LoadInstr,
    'BRA': BranchInstr,
    'BRZ': BranchZeroInstr,
    'BRP': BranchPosInstr,
    'INP': InputInstr,
    'OUT': OutputInstr,
    'OTC': OutputCharInstr,
}
VALID_NAMES: set[str] = set(NAME_TO_CLS_MAP.keys()) | {'DAT'}
REQUIRED_OPERAND: set[type[Instruction]] = {
    AddInstr,
    SubInstr,
    StoreInstr,
    LoadInstr,
    BranchInstr,
    BranchZeroInstr,
    BranchPosInstr,
}


# noinspection PyMethodMayBeStatic
class AsmParser:
    # yet another parser??!
    # NOTE: unrecognised instructions will often be interpreted as labels
    #  `HL` (typo, should be `HLT`) will be interpreted as a label
    def __init__(self, src: str, extensions=True, append_hlt=False):
        self.src = src
        self.extensions = extensions
        self.do_append_hlt = append_hlt
        self.instructions: list[Instruction | Data] = []
        self.memory: list[int] = []
        self.parsed_instr_ls: list[ParsedInstr] = []
        self.labels: dict[str, int] = {}
        self._queued_labels: set[str] = set()
        """Labels that will be attached to the next instruction"""

    def parse(self):
        self.parse_file()
        self.resolve_labels()
        self.generate_instructions()
        self.generate_memory()
        return self  # for convenience

    # region parse_file
    def parse_file(self):
        for line in self.src.splitlines():
            self.parse_line(line)
        self._finish_parse_file()

    def parse_line(self, line: str):
        line = line.strip()
        code, *_comment = line.split('//', maxsplit=1)
        code: str = code.strip()
        words = [w.strip() for w in code.split()]
        self._parse_words(words)

    def _parse_words(self, words: list[str]):
        match words:
            case [label, opcode, operand]:
                self._parse_3(label, opcode, operand)
            case [opcode, operand] if opcode in VALID_NAMES:
                self._parse_3(None, opcode, operand)
            case [label, opcode] if opcode in VALID_NAMES:
                self._parse_3(label, opcode, None)
            case [a, b]:
                raise AsmParseError(f"Invalid line in ASM: unknown opcode: "
                                    f"none of ({a!r}, {b!r}) is a valid opcode")
            case [opcode] if opcode in VALID_NAMES:
                self._parse_3(None, opcode, None)
            case [label]:
                self._parse_3(label, None, None)
            case []:
                pass
            case _: raise AsmParseError(
                "Invalid syntax: expected line to be "
                "[label] [opcode [operand]], space-separated")

    def _parse_3(self, label: str | None, opcode: str | None, operand: str | int | None):
        if label is not None:
            label = label.removesuffix(':')
            self._queued_labels.add(label)
        if opcode is None:
            assert operand is None
        else:
            self._parse_opcode_operand(opcode, operand)

    def _parse_opcode_operand(self, opcode: str, operand: str | int | None):
        if operand is not None:
            try:
                operand = int(operand)
            except ValueError:
                pass
        if opcode not in VALID_NAMES:
            raise AsmParseError(f"Invalid opcode: {opcode!r}")
        self._add_instruction(ParsedInstr(opcode, operand))

    def _add_instruction(self, instr: ParsedInstr):
        self.parsed_instr_ls.append(instr)
        self._attach_queued_labels()

    def _attach_queued_labels(self):
        last_idx = len(self.parsed_instr_ls) - 1
        last_instr = self.parsed_instr_ls[-1]
        for lb in self._queued_labels:
            if lb in self.labels:
                # Perhaps this could be done in a way that labels can be
                #  redeclared but that would be tricky as BRA can be backwards
                #  as well as forwards so don't know exactly when each label's
                #  area of effect starts and ends and I don't really want
                #  to add a new non-standard directive with the only
                #  purpose of separating label areas.
                # This can always be added later but can't be removed as easily
                #  due to backwards compatibility with the older versions.
                raise AsmParseError(f"Error: label `{lb}` used more than once")
            self.labels[lb] = last_idx
            last_instr.labels.add(lb)
        self._queued_labels.clear()

    def _finish_parse_file(self):
        if self.do_append_hlt:
            self._append_final_hlt()
            # queued labels should've been attached to the extra HLT
            assert len(self._queued_labels) == 0
        else:
            self._handle_leftover_queued_labels()

    def _append_final_hlt(self):
        self._add_instruction(ParsedInstr('HLT', 0))

    def _handle_leftover_queued_labels(self):
        idx_after_last = len(self.parsed_instr_ls)
        # don't add to the Instr as there is no ParsedInstr to add to
        #  and the .labels of the ParsedInstr is not actually used
        for lb in self._queued_labels:
            if lb in self.labels:
                raise AsmParseError(f"Error: label `{lb}` used more than once")
            self.labels[lb] = idx_after_last
        self._queued_labels.clear()
    # endregion

    # region resolve_labels
    def resolve_labels(self):
        for instr in self.parsed_instr_ls:
            if isinstance(instr.operand, str):
                instr.operand = self._resolve_label(instr.operand)

    def _resolve_label(self, label: str) -> int:
        try:
            return self.labels[label]
        except KeyError:
            raise AsmUnknownLabelError(f"Label {label!r} is not defined")
    # endregion

    # region generate_instructions
    def generate_instructions(self):
        for parsed in self.parsed_instr_ls:
            self.instructions.append(
                self._get_dat_instr(parsed) if parsed.opcode == 'DAT'
                else self._get_normal_instr(parsed))

    def _get_normal_instr(self, parsed: ParsedInstr):
        instr_cls = NAME_TO_CLS_MAP.get(parsed.opcode)
        if instr_cls is None:
            raise AsmParseError(f"Unknown opcode: {parsed.opcode}")
        if not self.extensions:
            self._raise_if_nonstandard_instr(instr_cls)
        if parsed.operand is None:
            if instr_cls in REQUIRED_OPERAND:
                raise AsmParseError(f"{parsed.opcode} requires an operand")
            return instr_cls.from_default_operand()
        assert isinstance(parsed.operand, int)
        return instr_cls.from_b10_operand(parsed.operand)

    def _raise_if_nonstandard_instr(self, instr_cls: type[Instruction]):
        if instr_cls == OutputCharInstr:
            raise ExtensionDisabledError(
                "The non-standard OTC instruction (code 922) is not "
                "enabled (HINT: pass extensions=True to enable it)")

    def _get_dat_instr(self, parsed: ParsedInstr):
        assert parsed.opcode == 'DAT'
        operand = 0 if parsed.operand is None else parsed.operand
        # labels should've been resolved already
        assert isinstance(operand, int)
        return Data(operand)
    # endregion

    def generate_memory(self):
        self.memory = instructions_to_memory(self.instructions)
