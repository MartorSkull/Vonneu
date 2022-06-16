#!/usr/bin/env python3
import re

from .utils import NUM_RE

class VonNeumannInstruction(object):
    instMatch = None
    syntMatch = None
    humInst = None
    next = None
    def __init__(self, inst, alph):
        self.inst = inst
        self.alph = alph
        self.instMatch = self.instMatch.format(alph=self.alph)
        self.syntMatch = self.syntMatch.format(alph=self.alph)
        self.match = re.fullmatch(self.syntMatch, inst)
        if (self.match is not None):
            self.args = list(map(int, self.match.groups()))
        else:
            raise SyntaxError(f"Unable to parse instruction: {self.inst}")

    def __str__(self):
        return self.humInst.format(*self.args)

    def __repr__(self):
        return self.humInst.format(*self.args)

    def get_used_vars(self):
        pass

    def __call__(self, numbs, words):
        ns, ws = self.effect(numbs, words)
        next = None
        if (self.next is not None):
            next = self.next
            self.next = None
        return (next, ns, ws)

    @classmethod
    def get_inst_re(cls, alph):
        return cls.instMatch.format(alph=alph)

    def _jump(self, label):
        self.next = label

class Suc(VonNeumannInstruction):
    instMatch = fr"N{NUM_RE}<-N{NUM_RE}\+1"
    syntMatch = fr"N(?P<PN>{NUM_RE})<-N(?P=PN)\+1"
    humInst = "N{0} <- N{0}+1"

    def effect(self, numbs, words):
        n = self.args[0]
        numbs[n] += 1
        return numbs, words

    def get_used_vars(self):
        return self.args, [], []

class Pred(VonNeumannInstruction):
    instMatch = fr"N{NUM_RE}<-N{NUM_RE}\.-1"
    syntMatch = fr"N(?P<MN>{NUM_RE})<-N(?P=MN)\.-1"
    humInst = "N{0} <- N{0}.-1"

    def effect(self, numbs, words):
        n = self.args[0]
        numbs[n] = max(numbs[n]-1,0)
        return numbs, words

    def get_used_vars(self):
        return self.args, [], []

class AssignNumber(VonNeumannInstruction):
    instMatch = fr"N{NUM_RE}<-N{NUM_RE}"
    syntMatch = fr"N({NUM_RE})<-N({NUM_RE})"
    humInst = "N{0} <- N{1}"

    def effect(self, numbs, words):
        numbs[self.args[0]] = numbs[self.args[1]]
        return numbs, words

    def get_used_vars(self):
        return self.args, [], []

class AssignZero(VonNeumannInstruction):
    instMatch = fr"N{NUM_RE}<-0"
    syntMatch = fr"N([0-9])+<-0"
    humInst = "N{0} <- 0"

    def effect(self, numbs, words):
        numbs[self.args[0]] = 0
        return numbs, words

    def get_used_vars(self):
        return self.args, [], []

class Ifneq0(VonNeumannInstruction):
    instMatch = fr"IFN{NUM_RE}\/=0GOTOL{NUM_RE}"
    syntMatch = fr"IFN({NUM_RE})\/=0GOTOL({NUM_RE})"
    humInst = "IF N{0} /= 0 GOTO L{1}"

    def effect(self, numbs, words):
        if (numbs[self.args[0]]!=0):
            self._jump(self.args[1])
        return numbs, words

    def get_used_vars(self):
        return [self.args[0]], [], [self.args[1]]

class Append(VonNeumannInstruction):
    instMatch = fr"P{NUM_RE}<-P{NUM_RE}.{{alph}}"
    syntMatch = fr"P(?P<WA>{NUM_RE})<-P(?P=WA).({{alph}})"
    humInst = "P{0} <- P{0}.{1}"

    def effect(self, numbs, words):
        words[self.args[0]] += self.args[1]
        return numbs, words

    def get_used_vars(self):
        return [], [self.args[0]], []

class Tail(VonNeumannInstruction):
    instMatch = fr"P{NUM_RE}<->P{NUM_RE}"
    syntMatch = fr"P(?P<WR>{NUM_RE})<->P(?P=WR)"
    humInst = "P{0} <- >P{0}"

    def effect(self, numbs, words):
        words[self.args[0]] = words[self.args[0]][1:]
        return numbs, words

    def get_used_vars(self):
        return [], self.args, []

class AssignWord(VonNeumannInstruction):
    instMatch = fr"P{NUM_RE}<-P{NUM_RE}"
    syntMatch = fr"P({NUM_RE})<-P({NUM_RE})"
    humInst = "P{0} <- P{1}"

    def effect(self, numbs, words):
        words[self.args[0]] = words[self.args[1]]
        return numbs, words

    def get_used_vars(self):
        return [], self.args, []

class AssignEpsilon(VonNeumannInstruction):
    instMatch = fr"P{NUM_RE}<-e"
    syntMatch = fr"P({NUM_RE})<-e"
    humInst = "P{0} <- e"

    def effect(self, numbs, words):
        words[self.args[0]] = ""
        return numbs, words

    def get_used_vars(self):
        return [], self.args, []

class Ifbeg(VonNeumannInstruction):
    instMatch = fr"IFP{NUM_RE}BEGINS{{alph}}?GOTOL{NUM_RE}"
    syntMatch = fr"IFP({NUM_RE})BEGINS({{alph}}?)GOTOL({NUM_RE})"
    humInst = "IF P{0} BEGINS {1} GOTO L{2}"

    def effect(self, numbs, words):
        a = words[self.args[0]]
        if (a!="" and a[0]==self.args[1]):
            self._jump(self.args[2])
        return numbs, words

    def get_used_vars(self):
        return [], [self.args[0]], [self.args[2]]


class Goto(VonNeumannInstruction):
    instMatch = fr"GOTOL{NUM_RE}"
    syntMatch = fr"GOTOL({NUM_RE})"
    humInst = "GOTO L{0}"

    def effect(self, numbs, words):
        self._jump(self.args[0])
        return numbs, words

    def get_used_vars(self):
        return [], [], self.args

class Skip(VonNeumannInstruction):
    instMatch = r"SKIP"
    syntMatch = r"SKIP"
    humInst = "SKIP"
    def __init__(self, inst="SKIP", alph="[]"):
        super().__init__(inst, alph)

    def effect(self, numbs, words):
        return numbs, words

    def get_used_vars(self):
        return [], [], []

class MacroCall(VonNeumannInstruction):
    instMatch = fr"\[.*?\]"
    humInst = "[{0}]"
    def __init__(self, inst, alph, macro_state, inside_macro):
        self.inst = inst
        self.name = inst[1:-1]
        self.alph = alph
        self.inside_macro = inside_macro
        self.macro = macro_state.match(self.name, inside_macro)

    def __str__(self):
        return self.humInst.format(self.name)

    def __repr__(self):
        return self.humInst.format(self.name)

    def effect(self, numbs, words):
        label, numbs, words = self.macro(numbs, words)
        if label is not None:
            self._jump(label)
        return numbs, words

    def get_used_vars(self):
        return self.macro.get_used_vars()

    def compile(self, used_vars):
        return self.macro.compile(used_vars)

    def parse_code(self):
        return self.macro.parse_code()

    @property
    def optimized(self):
        return self.macro.template.optimized

instruction_list = [Suc, Pred, AssignNumber, AssignZero, Ifneq0, Append, Tail,
                   AssignWord, AssignEpsilon, Ifbeg, Goto, Skip, MacroCall]

instruction_dict = {i.__name__:i for i in instruction_list}