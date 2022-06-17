#!/usr/bin/env python3
import re
import logging

from collections import defaultdict


from .instructions import *
from .utils import *
from .macros import *
from .parser import VonNeumannParser

class VonNeumannProgram(object):
    def __init__(self, program, settings):
        self.settings = settings
        self.program = program

        macro_re = fr"(?:{VonNeumannMacroTemplate.get_macro_re()})[ \n\t]*"
        self.code = re.split(
            macro_re,
            self.program,
            flags=re.MULTILINE | re.DOTALL)[-1]
        self.code = clean_program(self.code)

        macro_match = re.finditer(
            VonNeumannMacroTemplate.get_macro_re(),
            self.program,
            re.MULTILINE | re.DOTALL)

        self.macro_state = MacroState()
        for i in macro_match:
            self.macro_state.register_macro(
                VonNeumannMacroTemplate(i.group(),
                                        self.settings,
                                        self.macro_state)
            )

        self.parser = VonNeumannParser(self.code,
                                       self.settings,
                                       self.macro_state)

        self.instrs = [x[1] for x in self.parser.instrs]
        self.labels = {}
        for i,l in enumerate(self.parser.instrs):
            label = int(l[0]) if l[0] is not None else None
            if (label is not None) and (label not in self.labels):
                self.labels[label] = i
        logging.info(f"Expanded Program :\n{self.parser.get_program_str()}")

    def get_regex(self):
        if (hasattr(self,"_regex")):
            return self._regex
        r = gen_regex(self.settings.instrs, self.settings.alph)
        self._regex = r
        logging.debug(f"Language Regex={self._regex}")
        return r

    def __call__(self, numbs, words, ret, max_steps=None):
        logging.debug(f"Called => prog({numbs}, {words}, {ret})")
        return self.run(numbs, words, ret, max_steps)

    def _str_state(self, i, l, numbs, words):
        if (not hasattr(self,"n_inst")):
            self.n_inst = len(str(len(self.instrs)))
        form = (f"Executed => {i:^{self.n_inst}d}: {str(self.instrs[i])}")
        form = form+f"\tgoto={'L'+str(l) if l is not None else 'Next'}"
        form = form+(f"\tnumbs={dict(numbs.items())}" if numbs else "")
        form = form+(f"\twords={dict(words.items())}" if words else "")
        return form

    def run(self, ns, ws, ret, max_steps):
        numbs = defaultdict(lambda: 0)
        words = defaultdict(lambda: "")
        i=0
        # Initialize num state
        for i, n in enumerate(ns):
            numbs[i] = n
        # Initialize word state
        for i, w in enumerate(ws):
            words[i] = w
        # Main execution loop
        i = 0
        s = 0
        while i<len(self.instrs):
            # Exec instruction
            l, numbs, words = self.instrs[i](numbs, words)
            logging.info(self._str_state(i, l, numbs, words))
            # Jump to a label or to the next instruction
            if (l is not None):
                i = self.labels[l]
            else:
                i += 1
            if max_steps is not None and max_steps>=s:
                raise RuntimeError("Max ammount of steps reached")
            s+=1
        # Once finished return what was asked
        if (ret == 'n'):
            return numbs[0]
        elif (ret == 'w'):
            return words[0]

    def get_expanded_program(self):
        return self.parser.get_program_str()