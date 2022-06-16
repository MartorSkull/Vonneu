# Vonneu
A sigma-mixed Von Neumann imperative language

## Variables
There are no variables per-se. This language has 2 arrays that contain numbers and strings built from a given alphabet. We can access this values with `Nx` and `Px` respectively, replacing the `x` for the index. For example `N0 <- N0 + 1` will add 1 to the value on the index 0 of the number array. Example 2: `P0 <- P0.a` will add the character `a` to the end of the strings at index 0.

### Alphabet
The alphabet is passed through the command line when running the program with the cli argument `-a`. String values will only be able to contain these characters and nothing else.

## Program Flow
Instructions are executed secuentially, unless a `GOTO` instruction is executed or an `IF` instruction validates its condition. For these cases we use labels. An example of a label is `L0 N0 <- N0 + 1`, this instruction now has the label `L0` attached to it, when running `GOTO L0` the code will go to the instruction that posseses the L0 label.

## Instructions
There are 12 instructions for this language. 4 numeric, 4 for strings and 4 flow control:

### Numerical Instructions
* `Nx <- Nx + 1`: Successor function (Note: the variable has to be the same)
* `Nx <- Nx .- 1`: Predecesor function. It's limit is 0, if 0 is the value on `Nx` then the value will be unchanged.
* `Nx <- Ny`: Assignment (Note: we cannot insert expressions after instead of N1)
* `Nx <- 0`: Assign 0 (Note: we cannot assign other numbers to indexes on the list)

### String Instructions
* `Px <- Px.a`: Appends a character `a` to the end of the string (Note: this character must be one of the character in the alphabet)
* `Px <- >Px`: Removes the first character from the string.
* `Px <- Py`: Assigns the value of the second variable to the first
* `Px <- e`: Assigns the empty string to the index.

### Flow control Instructions
* `IF N0 /= 0 GOTO Lx`: Jumps to the instruction with the `Lx` label if the value on the index is different than 0.
* `IF P0 BEGINS a GOTO Lx`: Jumps to the instruction with the `Lx` label if the string on the index starts with `a` (same as the `P0 <- P0.a` the character must be on the alphabet.)
* `GOTO Lx`: Jumps to the instruction with the `Lx` label.
* `SKIP`: Does nothing and continues.

## Macros
This language allows users to define macros. Macros are code that can be expanded into the program. Macros are different to functions. Macros are not called, they modify the code where they are placed, functions jump into instructions to come back later and continue with the code.

### Variables
Variables in macros are different than the main code, the indexes in them are auxiliary. This means that when compiling the compiler will find an index that is not used by any other instruction and replace the auxiliary index with it. To note this we use `Vx` and `Wx` for numbers and strings respectively. For labels the laguage will do the same, the auxiliary label syntax is `Ax`.

Macros must be defined at the start of the file and posses the following syntax.
```
{Macro Name} {
    Macro Code
}
```
For example, `a` being a character in the alphabet:
```
{V1 <- V2+1} {
    V3 <- V2
    V3 <- V3 + 1
    V1 <- V3
}

{W1 <- W2.a} {
    W3 <- W2
    W3 <- W3.a
    W1 <- W3
}

{V1 A1} {
    V1 <- V1+1
    GOTO A1
}
```
The compiler will detect the variables in the name and use them as "Parameters" for the macro.

### Expanding macros
To expand macros we can insert `[Macro Name]` in the code. For example:
```
{V0 <- V1-1} {
    V2 <- V1
    V2 <- V2 .- 1
    V0 <- V3
}

[N1 <- N2-1]
L0 IF N1 /= 0 GOTO L1
GOTO L0
L1 SKIP

```
This code will be expanded as follows:
```
N0 <- N2
N0 <- N0 .- 1
N1 <- N0
L0 IF N1 /= 0 GOTO L1
GOTO L0
L1 SKIP
```

### Optimizing Macros
Since some of these operations, for example the sum of two variables, take thousands of instructions we are can write python code to make the code faster. For example

```
{V1<-V2+V3 THEN GOTO A0} {
    V4 <- V2
    V5 <- V3
    A3 IF V5 /= 0 GOTO A1
       GOTO A2
    A1 V5 <- V5 .- 1
       V4 <- V4 + 1
       GOTO A3
    A2 V1 <- V4
    GOTO A0
} !!
V[4] = V[2]+V[3]
V[5] = 0
V[1] = V[2]+V[3]
GOTO(A[0])
!!
```
This macro calculates the sum of two variables. To prevent the interpreter from running thousands of instructions we write the python code. Variables are the same as in the macro's vonneu code. To access a variable value use `V[x]` and `W[x]` for numbers and words repectively. To go to an outside label use the `GOTO` function with the `A[x]` as the argument for the label.

This code will not run unles the interpreter is started with the `-O1` argument.

## Whitespace
Whitespace is irrelevant except for the python optimized code. When interpreting the parser removes all whitespace.

## Running the interpreter
To run a program use the `vonneu.py` script. For example:
```
./vonneu.py -i examples/macro.vn -v DEBUG -a '[@#]' -O1 -r n -ns 123 2 -ws ##@@
```
Each argument has a different effect on the runtime. The arguments are:
* `-i` or `--input`: Input file. The file for the interpreter to run
* `-a` or `--alpha`: Alphabet. The alphabet to be used. Should be a regex match. Defautl: `[a-z0-9]`
* `-r` or `--ret`: return type. Can be either `n` for number or `w` for string.
* `-v` or `--verbosity`: Log level to print. Posible values are DEBUG, INFO, WARNING. On INFO the program will print the state changes.
* `-O`: Optimization. Choices are `0` to run pure vonneu code or `1` to use the optimized python code
* `-ns`: Numerical inputs. Numerical inputs for the program.
* `-ws`: String inputs. String inputs for the program.
* `-h` or `--help`: explanation of the arguments.

