#!/usr/bin/env python3

VAR_TP_CHAR = ["N", "P", "L"]
VAR_TP_INDX = { k:i for i,k in enumerate(VAR_TP_CHAR)}
AUX_TP_CHAR = ["V", "W", "A"]
AUX_TP_INDX = { k:i for i,k in enumerate(AUX_TP_CHAR)}
VAR_TO_AUX = {v:a for a,v in zip(AUX_TP_CHAR,VAR_TP_CHAR)}
AUX_TO_VAR = {a:v for a,v in zip(AUX_TP_CHAR,VAR_TP_CHAR)}

NUM_RE = r"(?:[1-9][0-9]*|0)"
VAR_MATCH = fr"([NPL])({NUM_RE})"
AUX_MATCH = fr"([VWA])({NUM_RE})"

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
        self.used_vars = [set(), set(), set()]

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

    def get_used_vars(self):
        return self.used_vars

    def get_free_vars(self, ammounts):
        for i, vars_tp, aux_tp in zip(range(3),
                                   self.used_vars,
                                   self.template.get_auxiliary()):
            end = max(vars_tp) if vars_tp else 0
            complete = set(range(0, end+ammounts[i]+1))
            diff = complete.difference(vars_tp)
        return diff

    def update_used_vars(self, used):
        for i in range(3):
            self.used_vars[i] = self.used_vars[i].union(set(used[i]))

    def take_var(self, tp, indx):
        taken = indx in self.used_vars[tp]
        self.used_vars[tp].add(indx)
        return taken

    def take_number(self, indx):
        return self.take_var(0, indx)

    def take_word(self, indx):
        return self.take_var(1, indx)

    def take_label(self, indx):
        return self.take_var(2, indx)