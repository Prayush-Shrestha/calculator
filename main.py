





# main.py



import customtkinter as ctk

from tkinter import messagebox

import math

import ast

import operator as op

from functools import partial



# ------------ Safe eval (same logic as CLI) ------------

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



def _eval_node(node):

    if isinstance(node, ast.Num):

        return node.n

    if hasattr(ast, "Constant") and isinstance(node, ast.Constant):

        if isinstance(node.value, (int, float)):

            return node.value

        raise ValueError("Invalid constant")

    if isinstance(node, ast.BinOp):

        left = _eval_node(node.left)

        right = _eval_node(node.right)

        o = type(node.op)

        if o in ALLOWED_BINOPS:

            return ALLOWED_BINOPS[o](left, right)

        raise ValueError("Operator not allowed")

    if isinstance(node, ast.UnaryOp):

        operand = _eval_node(node.operand)

        u = type(node.op)

        if u in ALLOWED_UNARYOPS:

            return ALLOWED_UNARYOPS[u](operand)

        raise ValueError("Unary op not allowed")

    if isinstance(node, ast.Call):

        if not isinstance(node.func, ast.Name):

            raise ValueError("Bad function call")

        fname = node.func.id

        if fname not in MATH_FUNCS:

            raise ValueError("Function not allowed")

        args = [_eval_node(a) for a in node.args]

        return MATH_FUNCS[fname](*args)

    raise ValueError("Unsupported node")



def safe_eval(expr):

    node = ast.parse(expr, mode="eval").body

    return _eval_node(node)



# ------------ GUI ------------

ctk.set_appearance_mode("Dark")

ctk.set_default_color_theme("dark-blue")



class FancyCalc(ctk.CTk):

    def __init__(self):

        super().__init__()

        self.title("Prayush calculator")

        self.geometry("550x620")

        self.minsize(360, 560)



        # state

        self.memory = 0.0

        self.last_result = None



        # layout: display on top, buttons grid below, right column history

        self.grid_columnconfigure(0, weight=1)

        self.grid_columnconfigure(1, weight=0)

        self.grid_rowconfigure(1, weight=1)



        # display frame

        disp_frame = ctk.CTkFrame(self, corner_radius=12)

        disp_frame.grid(row=0, column=0, columnspan=2, padx=12, pady=12, sticky="nwe")

        self.display = ctk.CTkEntry(disp_frame, font=ctk.CTkFont(size=22, weight="bold"))

        self.display.grid(row=0, column=0, padx=10, pady=14, sticky="we")

        self.display.bind("<Return>", lambda e: self.evaluate())

        self.display.bind("<Escape>", lambda e: self.clear_all())

        self.display.focus()



        # memory buttons

        mem_frame = ctk.CTkFrame(disp_frame, fg_color="transparent")

        mem_frame.grid(row=1, column=0, sticky="we", padx=6)

        self.mem_label = ctk.CTkLabel(mem_frame, text="M: 0", width=120)

        self.mem_label.grid(row=0, column=0, padx=(0,6))

        ctk.CTkButton(mem_frame, text="M+", width=60, command=self.mem_add).grid(row=0, column=1, padx=4)

        ctk.CTkButton(mem_frame, text="M-", width=60, command=self.mem_sub).grid(row=0, column=2, padx=4)

        ctk.CTkButton(mem_frame, text="MR", width=60, command=self.mem_recall).grid(row=0, column=3, padx=4)

        ctk.CTkButton(mem_frame, text="MC", width=60, command=self.mem_clear).grid(row=0, column=4, padx=4)



        # Buttons grid

        btn_frame = ctk.CTkFrame(self, corner_radius=12)

        btn_frame.grid(row=1, column=0, padx=(12,6), pady=6, sticky="nsew")

        for i in range(6):

            btn_frame.grid_rowconfigure(i, weight=1)

        for j in range(4):

            btn_frame.grid_columnconfigure(j, weight=1)



        buttons = [

            ("7","8","9","/"),

            ("4","5","6","*"),

            ("1","2","3","-"),

            ("0",".","(","+"),

            (")","**","%","//"),

            ("sqrt(","fact(","log(","=")

        ]

        for r, row in enumerate(buttons):

            for c, label in enumerate(row):

                action = partial(self.on_button, label)

                if label == "=":

                    btn = ctk.CTkButton(btn_frame, text=label, command=self.evaluate, corner_radius=10)

                else:

                    btn = ctk.CTkButton(btn_frame, text=label, command=action, corner_radius=10)

                btn.grid(row=r, column=c, padx=6, pady=6, sticky="nsew")



        # right panel: history and controls

        right = ctk.CTkFrame(self, width=200, corner_radius=12)

        right.grid(row=1, column=1, padx=(6,12), pady=6, sticky="nsew")

        right.grid_rowconfigure(1, weight=1)

        ctk.CTkLabel(right, text="History", font=ctk.CTkFont(size=16, weight="bold")).grid(row=0, column=0, padx=8, pady=(8,4))

        self.hist_box = ctk.CTkTextbox(right, width=220, wrap="word", state="disabled")

        self.hist_box.grid(row=1, column=0, padx=8, pady=6, sticky="nsew")

        ctk.CTkButton(right, text="Clear History", command=self.clear_history).grid(row=2, column=0, padx=8, pady=(4,10), sticky="we")



        # footer controls

        foot = ctk.CTkFrame(self, fg_color="transparent")

        foot.grid(row=2, column=0, columnspan=2, pady=(0,12))

        ctk.CTkButton(foot, text="Clear", width=100, command=self.clear_entry).grid(row=0, column=0, padx=8)

        ctk.CTkButton(foot, text="All Clear", width=100, command=self.clear_all).grid(row=0, column=1, padx=8)



    # ---------- button handlers ----------

    def on_button(self, text):

        # insert the button text into entry

        cur = self.display.get()

        self.display.delete(0, "end")

        self.display.insert(0, cur + text)



    def evaluate(self):

        expr = self.display.get().strip()

        if not expr:

            return

        # replace ANS and MEM tokens

        expr = expr.replace("ANS", str(self.last_result) if self.last_result is not None else "0")

        expr = expr.replace("MEM", str(self.memory))

        try:

            res = safe_eval(expr)

            # format result

            if isinstance(res, float) and res.is_integer():

                res = int(res)

            self.last_result = res

            self.display.delete(0, "end")

            self.display.insert(0, str(res))

            self.append_history(expr, res)

        except Exception as e:

            messagebox.showerror("Error", f"Could not evaluate: {e}")



    def append_history(self, expr, res):

        self.hist_box.configure(state="normal")

        self.hist_box.insert("end", f"{expr} = {res}\n")

        self.hist_box.see("end")

        self.hist_box.configure(state="disabled")



    def clear_history(self):

        self.hist_box.configure(state="normal")

        self.hist_box.delete("1.0", "end")

        self.hist_box.configure(state="disabled")



    def clear_entry(self):

        self.display.delete(0, "end")



    def clear_all(self):

        self.display.delete(0, "end")

        self.last_result = None



    # ---------- memory ----------

    def mem_add(self):

        if self.last_result is None:

            messagebox.showinfo("Memory", "No last result to add.")

            return

        self.memory += float(self.last_result)

        self.mem_label.configure(text=f"M: {self.memory}")



    def mem_sub(self):

        if self.last_result is None:

            messagebox.showinfo("Memory", "No last result to sub.")

            return

        self.memory -= float(self.last_result)

        self.mem_label.configure(text=f"M: {self.memory}")



    def mem_recall(self):

        self.display.delete(0, "end")

        self.display.insert(0, str(self.memory))

        self.last_result = self.memory



    def mem_clear(self):

        self.memory = 0.0

        self.mem_label.configure(text=f"M: {self.memory}")



if __name__ == "__main__":

    app = FancyCalc()

    app.mainloop() 