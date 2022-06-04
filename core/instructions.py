#!/usr/bin/env python3
import logging
import re

class VonNeumannInstruction(object):
    instMatch = None
    syntMatch = None
    next = None
    def __init__(self, inst, alph):
        self.inst = inst
        self.alph = alph
        self.instMatch = self.instMatch.format(alph=self.alph)
        self.syntMatch = self.syntMatch.format(alph=self.alph)
        self.match = re.fullmatch(self.syntMatch, inst)
        if (self.match is not None):
            self.args = self.match.groups()
        else:
            raise SyntaxError(f"Unable to parse instruction: {self.inst}")

    def __str__(self):
        return self.inst

    def __repr__(self):
        return self.inst

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

    def get_label(self):
        return self.args[0]

class Suc(VonNeumannInstruction):
    instMatch = r"N[0-9]+<-N[0-9]+\+1"
    syntMatch = r"N(?P<PN>[0-9]+)<-N(?P=PN)\+1"

    def effect(self, numbs, words):
        n = self.args[0]
        numbs[n] += 1
        return numbs, words

class Pred(VonNeumannInstruction):
    instMatch = r"N[0-9]+<-N[0-9]+-1"
    syntMatch = r"N(?P<MN>[0-9]+)<-N(?P=MN)-1"

    def effect(self, numbs, words):
        n = self.args[0]
        numbs[n] = max(numbs[n]-1,0)
        return numbs, words

class AssignNumber(VonNeumannInstruction):
    instMatch = r"N[0-9]+<-N[0-9]+"
    syntMatch = r"N([0-9]+)<-N([0-9]+)"

    def effect(self, numbs, words):
        numbs[self.args[0]] = numbs[self.args[1]]
        return numbs, words

class AssignZero(VonNeumannInstruction):
    instMatch = r"N[0-9]+<-0"
    syntMatch = r"N([0-9])+<-0"

    def effect(self, numbs, words):
        numbs[self.args[0]] = 0
        return numbs, words

class Ifneq0(VonNeumannInstruction):
    instMatch = r"IFN[0-9]+\/=0GOTOL[0-9]+"
    syntMatch = r"IFN([0-9]+)\/=0GOTOL([0-9]+)"

    def effect(self, numbs, words):
        if (numbs[self.args[0]]!=0):
            self._jump(self.args[1])
        return numbs, words

class Append(VonNeumannInstruction):
    instMatch = r"P[0-9]+<-P[0-9]+.{alph}"
    syntMatch = r"P(?P<WA>[0-9]+)<-P(?P=WA).({alph})"

    def effect(self, numbs, words):
        words[self.args[0]] += self.args[1]
        return numbs, words

class Tail(VonNeumannInstruction):
    instMatch = r"P[0-9]+<->P[0-9]+"
    syntMatch = r"P(?P<WR>[0-9]+)<->P(?P=WR)"

    def effect(self, numbs, words):
        words[self.args[0]] = words[self.args[0]][1:]
        return numbs, words

class AssignWord(VonNeumannInstruction):
    instMatch = r"P[0-9]+<-P[0-9]+"
    syntMatch = r"P([0-9]+)<-P([0-9]+)"

    def effect(self, numbs, words):
        words[self.args[0]] = words[self.args[1]]
        return numbs, words

class AssignEpsilon(VonNeumannInstruction):
    instMatch = r"P[0-9]+<-e"
    syntMatch = r"P([0-9]+)<-e"

    def effect(self, numbs, words):
        words[self.args[0]] = ""
        return numbs, words

class Ifbeg(VonNeumannInstruction):
    instMatch = r"IFP[0-9]+BEGINS{alph}?GOTOL[0-9]+"
    syntMatch = r"IFP([0-9]+)BEGINS({alph}?)GOTOL([0-9]+)"

    def effect(self, numbs, words):
        a = words[self.args[0]]
        if (a!="" and a[0]==self.args[1]):
            self._jump(self.args[2])
        return numbs, words


class Goto(VonNeumannInstruction):
    instMatch = r"GOTOL[0-9]+"
    syntMatch = r"GOTOL([0-9]+)"

    def effect(self, numbs, words):
        self._jump(self.args[0])
        return numbs, words

class Skip(VonNeumannInstruction):
    instMatch = r"SKIP"
    syntMatch = r"SKIP"

    def effect(self, numbs, words):
        return numbs, words

instruction_list = [Suc, Pred, AssignNumber, AssignZero, Ifneq0, Append, Tail,
                   AssignWord, AssignEpsilon, Ifbeg, Goto, Skip]

instruction_dict = {i.__name__:i for i in instruction_list}