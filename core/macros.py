#!/usr/bin/env python3
import re

from .parser import *
from .utils import *

class VonNeumannMacroTemplate(object):
    match = r"(?:{(.*?)}[ \n]*)(?:{(.*?)}[ \n]*)(?:!!(.*?)!!)?"
    opt_code = None
    def __init__(self, macro, settings, macro_state):
        self.settings = settings
        self.macro_state = macro_state
        match = re.fullmatch(self.match, macro, re.MULTILINE | re.DOTALL)
        if (not match):
            raise SyntaxError("Could not match a macro.")
        self.name = clean_program(match.group(1))

        self.code = clean_program(match.group(2))
        self.optimized = False
        if (match.group(3)):
            self.opt_code = match.group(3)
            self.optimized = True

    def get_vars_on_name(self):
        if (hasattr(self, "vars_on_name")):
            return self.vars_on_name
        self.vars_on_name = ([], [], [])
        varis = re.finditer(AUX_MATCH, self.name)
        for i in varis:
            var = i.group(2)
            tp = i.group(1)
            self.vars_on_name[AUX_TP_INDX[tp]].append(var)
        return self.vars_on_name

    def get_parameters(self):
        if (hasattr(self,"parameters")):
            return self.parameters
        vars = self.get_vars_on_name()
        self.parameters = ([],[],[])
        for i, v in enumerate(vars):
            seen = set()
            for j in v:
                if (j not in seen):
                    seen.add(j)
                    self.parameters[i].append(int(j))
        return self.parameters

    def get_auxiliary(self):
        if not hasattr(self,"auxiliary"):
            matches = re.finditer(AUX_MATCH, self.code)
            aux = (set(),set(),set())
            for match in matches:
                tp = match.group(1)
                var = int(match.group(2))
                if (tp=='V'):
                    aux[0].add(var)
                elif (tp=='W'):
                    aux[1].add(var)
                else:
                    aux[2].add(var)
            params = self.get_parameters()
            self.auxiliary = tuple(
                aux[i].difference(set(params[i])) for i in range(3)
            )
        return self.auxiliary

    def get_syntmatch(self):
        if (hasattr(self, "syntMatch")):
            return self.syntMatch
        self.syntMatch = re.escape(self.name)
        for vars, a, v in zip(self.get_vars_on_name(),
                              ("V", "W", "A"),
                              ("N", "P", "L")):
            seen = set()
            dupes = [x for x in vars if x in seen or seen.add(x)]
            for i in vars:
                var = f"{a}{i}"
                if (i in dupes):
                    self.syntMatch = self.syntMatch.replace(
                        var,
                        f"({v})(?P<{var.lower()}>[0-9]*)",
                        1)
                    self.syntMatch = self.syntMatch.replace(
                        var,
                        f"{v}(?P={var.lower()})")
                else:
                    self.syntMatch = self.syntMatch.replace(
                        var,
                        f"({v})([0-9]*)")
        return self.syntMatch

    def match_inst(self, inst):
        match = re.fullmatch(self.get_syntmatch(), inst)
        if (match is not None):
            return VonNeumannMacro(inst, self)

    @staticmethod
    def get_macro_re():
        return r"(?:{.*?}[ \n]*){2}(?:!!.*?!!)?"

class VonNeumannMacro:
    def __init__(self,
                 inst: str,
                 template: VonNeumannMacroTemplate):
        self.inst = inst
        self.code = template.code
        self.template = template
        self.compiled = False
        self.var_map = [dict(), dict(), dict()]
        self.parsed_insts = None
        self.ctx_used_vars = None

        match = re.fullmatch(self.template.get_syntmatch(), self.inst)
        arguments = ([], [], [])
        for i in range(1, len(match.groups())+1, 2):
            tp = match.group(i)
            var = match.group(i+1)
            arguments[VAR_TP_INDX[tp]].append(int(var))

        for i, args_tp, para_tp in zip(range(3),
                                    arguments,
                                    self.template.get_parameters()):
            for arg, para in zip(args_tp, para_tp):
                self.var_map[i][para] = arg

    def get_used_vars(self):
        return tuple( set(x.values()) for x in self.var_map )

    def compile(self):
        if self.compiled:
            return
        self.compiled = True
        for i, vars_tp, aux_tp in zip(range(3),
                                   self.template.macro_state.get_used_vars(),
                                   self.template.get_auxiliary()):
            end = max(vars_tp) if vars_tp else 0
            complete = set(range(0, end+len(aux_tp)+1))
            diff = complete.difference(vars_tp)
            for code, mape in zip(aux_tp, diff):
                self.var_map[i][code] = mape
                self.template.macro_state.take_var(i,code)


        self.code = re.sub(
            fr"([VWA])({NUM_RE})",
            self._translate_aux_var,
            self.code)

    def _translate_aux_var(self, match):
        var_tp = AUX_TO_VAR[match.group(1)]
        var_ind = self.var_map[VAR_TP_INDX[var_tp]][int(match.group(2))]
        return f"{var_tp}{var_ind}"

    def parse_code(self):
        if not self.compiled:
            raise MacroError("Can't parse instructions before compiling")
        self.code_parser = VonNeumannParser(self.code,
                                            self.template.settings,
                                            self.template.macro_state,
                                            self)
        return self.code_parser.instrs

    def __call__(self, numbs, words):
        V = OptCodeVariables(self.var_map[0], numbs)
        W = OptCodeVariables(self.var_map[1], words)
        out_labels = {}
        for k, v in self.var_map[2].items():
            if k in self.template.get_parameters()[2]:
                out_labels[k] = v
        A = OptCodeLabels(out_labels)
        GOTO = self._jump
        label = None
        try:
            exec(self.template.opt_code)
        except OutsideJump as e:
            label = e.args[0]
        return label, numbs, words

    def _jump(self, label):
        lab = label
        raise OutsideJump(lab)

class OptCodeLabels:
    """This class represents the labels inside the optimized code"""
    def __init__(self, var_map):
        self.var_map = var_map

    def __getitem__(self, key):
        if (isinstance(key, slice)):
            raise RuntimeError(
                "Slices not suported for optimized code variables")
        try:
            return self.var_map[key]
        except KeyError as e:
            raise IndexError(e.msg) from None

class OptCodeVariables:
    """This class represents the list of variables inside the optimized code"""
    def __init__(self, var_map, vars):
        self.vars = vars
        self.var_map = var_map

    def __getitem__(self, key):
        if (isinstance(key, slice)):
            raise RuntimeError(
                "Slices not suported for optimized code variables")
        try:
            return self.vars[self.var_map[key]]
        except KeyError as e:
            raise IndexError(e.msg) from None

    def __setitem__(self, key, value):
        if (isinstance(key, slice)):
            raise RuntimeError(
                "Slices not suported for optimized code variables")
        try:
            self.vars[self.var_map[key]] = value
        except KeyError as e:
            raise IndexError(e.msg()) from None

class MacroError(Exception):
    """Used when mistakes are made in the Macro class usage"""

class OutsideJump(Exception):
    """Used when a jump to an outside label is called from a macro optimized code"""