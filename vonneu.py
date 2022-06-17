#!/usr/bin/env python3

import logging
import argparse
import sys

from core import *
from core import instructions
from core.utils import LanguageSettings, clean_program

aparser = argparse.ArgumentParser(
    description="Process and interpret Sigma-Von Neumann imperative Programs"
    )
aparser.add_argument("-i", "--input",
    metavar="I",
    type=open,
    required=True,
    help="Input program file"
    )
aparser.add_argument("-a", "--alpha",
    metavar="A",
    type=str,
    default="[a-z0-9]",
    help="The program's alphabet. Use regex sets. Ex: [@#] or [a-z]."
         " Default [a-z0-9]. Mayus are discouraged."
    )
aparser.add_argument("-r", "--ret",
    metavar="[nw]",
    type=str,
    default="n",
    choices="nw",
    help="Return value. Either n (number) or w (word). Default n."
    )
aparser.add_argument("-v", "--verbosity",
    metavar="V",
    type=str,
    default="WARNING",
    choices=["DEBUG", "INFO", "WARNING"],
    help="Logging verbosity. DEBUG, INFO, WARNING are available."
    )
aparser.add_argument("-O",
    metavar="O",
    type=int,
    default=0,
    choices=[0,1],
    help="Optimaziations. Setting this to 1 will use the macro's python code")
aparser.add_argument("-m", "--max-steps",
    metavar="M",
    type=int,
    default=None,
    help="Max ammount of steps to run the program"
)
aparser.add_argument('-ns',
    metavar='N',
    type=int,
    nargs='*',
    default=[],
    help="Numeric arguments."
    )
aparser.add_argument('-ws',
    metavar='W',
    type=str,
    nargs="*",
    default=[],
    help="Word arguments."
    )

if __name__=="__main__":
    args = aparser.parse_args()

    numeric_level = getattr(logging, args.verbosity, None)
    logging.basicConfig(level=numeric_level)
    if (numeric_level>10):
        sys.tracebacklimit = -1

    logging.debug(f"Arguments: {args}")
    prog = args.input.read()
    logging.debug(f"Program: {prog}")
    settings = LanguageSettings(args.alpha, instructions.instruction_dict, args.O)
    for s in args.ws:
        for c in s:
            if (c not in args.alpha):
                raise ValueError(
                    "Words passed to the program must be on the given alphabet"
                    f"({args.alpha})")
    program = VonNeumannProgram(prog, settings=settings)
    print(program(args.ns, args.ws, args.ret, args.max_steps))