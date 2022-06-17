#!/usr/bin/env python3
import re
import logging


from .utils import *
from .instructions import *

class VonNeumannParser(object):
    def __init__(self,
                 code: str,
                 settings: LanguageSettings,
                 macro_state: MacroState=None,
                 inside_macro=None):
        self.code = clean_program(code)
        self.settings = settings
        self.macro_state = macro_state
        self.inside_macro = inside_macro
        self._parse_program()

    def _parse_program(self):
        non_parsed_insts = re.finditer(self.get_regex(), self.code)

        self.instrs = []
        last_stop = 0
        for i, m in enumerate(non_parsed_insts):
            span = m.span()
            # Check that the entire string was matched
            if (last_stop!=span[0]):
                raise SyntaxError(
                    f"On instruction {i+1}: Could not "
                    f"match {self.code[last_stop:span[0]]}"
                )
            last_stop = span[1]
            g = m.lastgroup
            try:
                inst_cls = self.settings.instrs[g]
                inst = inst_cls(m.group(g),
                                self.settings.alph,
                                self.macro_state,
                                self.inside_macro)
            except SyntaxError as e:
                raise SyntaxError(f"On line {i+1}. {e.msg}")

            l = m.group(1)
            if (l is not None):
                l = int(l)
                self.macro_state.take_label(l)
            self.instrs.append((l, inst))

        for i, linst in enumerate(self.instrs):
            l = linst[0]
            inst = linst[1]
            if (isinstance(inst,MacroCall)):
                inst.compile()
                if (self.settings.optim==0 or not inst.optimized):
                    macro_inst = inst.parse_code()
                    if l is not None:
                        s = Skip(
                            "SKIP",
                            self.settings.alph,
                            self.macro_state,
                            self.inside_macro)
                        macro_inst = [(l, s)]+macro_inst
                    self.instrs[i:i+1] = macro_inst

    def get_regex(self):
        if (hasattr(self,"_regex")):
            return self._regex
        r = gen_regex(self.settings.instrs, self.settings.alph)
        self._regex = r
        logging.debug(f"Language Regex={self._regex}")
        return r

    def get_program_str(self):
        program = ""
        for l,i in self.instrs:
            if l is not None:
                program += f"L{l} "
            program += f"{str(i)}\n"
        return program