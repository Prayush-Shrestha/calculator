main_cli.py

import ast

import math

import operator as op

from collections import deque



# Allowed operators map

ALLOWED_BINOPS = {

    ast.Add: op.add,

    ast.Sub: op.sub,

    ast.Mult: op.mul,

    ast.Div: op.truediv,

    ast.FloorDiv: op.floordiv,

    ast.Mod: op.mod,

    ast.Pow: op.pow,

}



ALLOWED_UNARYOPS = {

    ast.UAdd: lambda x: +x,

    ast.USub: lambda x: -x,

}



# Allowed math functions

MATH_FUNCS = {

    "sqrt": math.sqrt,

    "sin": math.sin,

    "cos": math.cos,

    "tan": math.tan,

    "log": lambda x, base=10: math.log(x, base),

    "ln": math.log,

    "exp": math.exp,

    "abs": abs,

    "fact": math.factorial,

    "factorial": math.factorial,

    "round": round,

}



# Safe eval using AST

def safe_eval(expr: str):

    """

    Evaluate arithmetic expressions safely.

    Supports numbers, parentheses, binops in ALLOWED_BINOPS, unary ops,

    and calls to allowed MATH_FUNCS.

    """

    try:

        node = ast.parse(expr, mode="eval").body

        return _eval_node(node)

    except Exception as e:

        raise ValueError(f"Invalid expression: {e}")



def _eval_node(node):

    if isinstance(node, ast.Num):  # python <3.8

        return node.n

    if hasattr(ast, "Constant") and isinstance(node, ast.Constant):  # py3.8+

        if isinstance(node.value, (int, float)):

            return node.value

        else:

            raise ValueError("Unsupported constant type.")

    if isinstance(node, ast.BinOp):

        left = _eval_node(node.left)

        right = _eval_node(node.right)

        op_type = type(node.op)

        if op_type in ALLOWED_BINOPS:

            return ALLOWED_BINOPS[op_type](left, right)

        else:

            raise ValueError("Operator not allowed.")

    if isinstance(node, ast.UnaryOp):

        operand = _eval_node(node.operand)

        utype = type(node.op)

        if utype in ALLOWED_UNARYOPS:

            return ALLOWED_UNARYOPS[utype](operand)

        raise ValueError("Unary operator not allowed.")

    if isinstance(node, ast.Call):

        if not isinstance(node.func, ast.Name):

            raise ValueError("Only simple function calls allowed.")

        fname = node.func.id

        if fname not in MATH_FUNCS:

            raise ValueError(f"Function '{fname}' not allowed.")

        args = [_eval_node(a) for a in node.args]

        # support keyword defaults? not necessary now

        return MATH_FUNCS[fname](*args)

    raise ValueError(f"Unsupported expression node: {type(node)}")



# CLI calculator main loop

def cli_main():

    print("FuzzuTech - Advanced CLI Calculator")

    print("Type expressions like: 2 + 3*4, sqrt(16), log(100,10), factorial(5)")

    print("Memory commands: M+ (add result), M- (sub result), MR (recall), MC (clear)")

    print("Other: hist (show history), clear (clear history), exit (quit), help")

    memory = 0.0

    last_result = None

    history = deque(maxlen=200)



    while True:

        try:

            inp = input(">>> ").strip()

        except (EOFError, KeyboardInterrupt):

            print("\nExiting.")

            break

        if not inp:

            continue



        cmd = inp.lower()



        if cmd == "exit":

            print("Bye!")

            break

        if cmd == "help":

            print("Examples: 3+4*2, (2+3)**2, sqrt(25), log(100,10)")

            print("Memory: M+, M-, MR, MC")

            continue

        if cmd == "hist":

            if not history:

                print("No history yet.")

            else:

                for i, (expr, res) in enumerate(history, start=1):

                    print(f"{i}. {expr} = {res}")

            continue

        if cmd == "clear":

            history.clear()

            print("History cleared.")

            continue



        # Memory commands

        if cmd.upper() in {"M+", "M-", "MR", "MC"}:

            c = cmd.upper()

            if c == "M+":

                if last_result is None:

                    print("No last result to add to memory.")

                else:

                    memory += float(last_result)

                    print(f"Memory = {memory}")

            elif c == "M-":

                if last_result is None:

                    print("No last result to subtract from memory.")

                else:

                    memory -= float(last_result)

                    print(f"Memory = {memory}")

            elif c == "MR":

                print(f"Memory Recall => {memory}")

                last_result = memory

            elif c == "MC":

                memory = 0.0

                print("Memory cleared.")

            continue



        # Evaluate expression

        try:

            # allow using 'ANS' or 'ans' to refer to last result and 'MEM' to memory

            expr = inp.replace("ANS", str(last_result) if last_result is not None else "0")

            expr = expr.replace("ans", str(last_result) if last_result is not None else "0")

            expr = expr.replace("MEM", str(memory))

            result = safe_eval(expr)

            # floatify small ints to int for clean display

            if isinstance(result, float) and result.is_integer():

                result = int(result)

            print(result)

            history.append((inp, result))

            last_result = result

        except Exception as e:

            print("Error:", e)



if __name__ == "__main__":

    cli_main() 

