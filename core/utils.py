#!/usr/bin/env python3

VAR_TP_CHAR = ["N", "P", "L"]
VAR_TP_INDX = { k:i for i,k in enumerate(VAR_TP_CHAR)}
AUX_TP_CHAR = ["V", "W", "A"]
AUX_TP_INDX = { k:i for i,k in enumerate(AUX_TP_CHAR)}
VAR_TO_AUX = {v:a for a,v in zip(AUX_TP_CHAR,VAR_TP_CHAR)}
AUX_TO_VAR = {a:v for a,v in zip(AUX_TP_CHAR,VAR_TP_CHAR)}

NUM_RE = r"(?:[1-9][0-9]*|0)"

def gen_regex(inst, alph):
    r = r"(?:L([0-9]+))?(?:"
    for k,i in inst.items():
        r += f"(?P<{k}>{i.get_inst_re(alph)})|"
    r = r[:-1]
    r += r")"
    return r

def clean_program(program: str):
    return program.replace(" ", "").replace("\n", "").replace("\t", "")

class LanguageSettings(object):
    def __init__(self, alph, instrs, optim=0):
        self.alph = alph
        self.instrs = instrs
        self.optim = optim

class MacroState(object):
    def __init__(self):
        self.macros = []

    def register_macro(self, macro):
        self.macros.append(macro)

    def match(self, macro, inside_macro=None):
        if inside_macro:
            stop = self.macros.index(inside_macro.template)
        else:
            stop = len(self.macros)
        for i in self.macros[:stop]:
            inst = i.match_inst(macro)
            if (inst is not None):
                return inst
        raise SyntaxError(f"Could not match macro {macro}")