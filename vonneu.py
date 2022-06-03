import logging
import argparse

from core.language import *

def clean_program(program: str):
    return program.replace(" ", "").replace("\n", "").replace("\t", "")

aparser = argparse.ArgumentParser(
    description="Process and interpret Sigma Von Neumann Programs"
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
    required=True,
    help="The program's alphabet. You can use regex sets. Ex: [@#] or [A-Z]."
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
    help="Logging verbosity. Can be DEBUG, INFO, WARNING."
    )
aparser.add_argument('-ns',
    metavar='N',
    type=int,
    nargs='*',
    help="Numeric arguments."
    )
aparser.add_argument('-ws',
    metavar='W',
    type=str,
    nargs="*",
    help="Word arguments."
    )

if __name__=="__main__":
    args = aparser.parse_args()

    loglevel = args.verbosity
    numeric_level = getattr(logging, loglevel, None)
    if not isinstance(numeric_level, int):
        raise ValueError(f"Invalid log level: {loglevel}")
    logging.basicConfig(level=numeric_level)

    prog = clean_program(args.input.read())
    program = VonNeumannLanguage(prog, alph=args.alpha)
    print(program(args.ns, args.ws, args.ret))