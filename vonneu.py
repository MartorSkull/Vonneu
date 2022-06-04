#!/usr/bin/env python3

import logging
import argparse
import sys

from core.language import *

def clean_program(program: str):
    return program.replace(" ", "").replace("\n", "").replace("\t", "")

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
    help="The program's alphabet. You can use regex sets. Ex: [@#] or [A-Z]."
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
    prog = clean_program(args.input.read())
    logging.debug(f"Program: {prog}")
    program = VonNeumannLanguage(prog, alph=args.alpha)
    print(program(args.ns, args.ws, args.ret))