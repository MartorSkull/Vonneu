#!/usr/bin/env python3
import re
import logging

from collections import defaultdict

from .instructions import *


class VonNeumannLanguage(object):
    def __init__(self, program, alph=r"[A-Za-z0-9]"):
        self.alph = alph
        logging.debug(f"Language Regex={self.get_regex()}")
        non_parsed_insts = re.finditer(self.get_regex(), program)
        self.instrs = []
        self.labels = {}
        for i, m in enumerate(non_parsed_insts):
            g = m.lastgroup
            self.instrs.append(instruction_dict[g](m.group(g), self.alph))
            label = m.group(1)
            if (label is not None):
                self.labels[label] = i
        logging.debug(f"Instructions={self.instrs}")
        logging.debug(f"Labels={self.labels}")

    def get_regex(self):
        if (hasattr(self,"_regex")):
            return self._regex
        r = r"(?:L([0-9]+))?(?:"
        for k,i in instruction_dict.items():
            r += f"(?P<{k}>{i.get_inst_re(self.alph)})|"
        r = r[:-1]
        r += r")"
        self._regex = r
        return r

    def __call__(self, numbs, words, ret):
        logging.debug(f"Called => prog({numbs}, {words}, {ret})")
        return self.run(numbs, words, ret=ret)

    def _str_state(self, i, l, numbs, words):
        return (f"Executed => {i:3d}: {str(self.instrs[i])+' =':20s}"
                f"goto={'L'+l if l else l}, "
                f"\tnums={dict(numbs.items())}, "
                f"\twords={dict(words.items())}")

    def run(self, ns, ws, ret):
        numbs = defaultdict(lambda: 0)
        words = defaultdict(lambda: "")
        i=0
        # Initialize num state TODO MAKE THIS BETTER
        for i, n in enumerate(ns):
            numbs[str(i)] = n
        # Initialize word state
        for i, w in enumerate(ws):
            words[str(i)] = w
        # Main execution loop
        i = 0
        while (i<len(self.instrs)):
            # Exec instruction
            l, numbs, words = self.instrs[i](numbs, words)
            logging.info(self._str_state(i, l, numbs, words))
            # Jump to a label or to the next instruction
            if (l is not None):
                i = self.labels[l]
            else:
                i += 1
        # Once finished return what was asked
        if (ret == 'n'):
            return numbs['0']
        elif (ret == 'w'):
            return words['0']
