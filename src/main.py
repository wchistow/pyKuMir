import tkinter

from lexer import KuMirLexer

VERSION = '1.0.0a0'


class Interface:
    def __init__(self):
        self.tk = tkinter.Tk()
        self.tk.title(f'pyKuMir v{VERSION}')
        self.lexer = KuMirLexer()
        self.codeinput = tkinter.Text(self.tk, tabs=2)
        self.codeinput.grid(row=1, column=1, columnspan=2)
        self.codeinput.tag_configure("Token.Keyword", foreground="red")
        self.codeinput.tag_configure("Token.Text", foreground="black")
        self.codeinput.tag_configure("Token.Literal.String", foreground='orange')
        self.codeinput.tag_configure("Token.Comment", foreground="grey")
        self.codeinput.bind('<Key>', lambda event: self.tk.after(20,
                            self.highlight_syntax))

        tkinter.mainloop()

    def highlight_syntax(self):
        for tag in ("Token.Keyword", "Token.Text", "Token.Literal.String",
                    "Token.Comment", "Token.Name.Builtin", "Token.Number"):
            self.codeinput.tag_remove(tag, "1.0", "end")
        name_entered = self.codeinput.get("1.0", "end")
        self.codeinput.mark_set("range_start", "1.0")
        for start, token, token_text in self.lexer.get_tokens_unprocessed(name_entered):
            self.codeinput.mark_set("range_end", f"range_start + {len(token_text)}c")
            self.codeinput.tag_add(str(token), 'range_start', 'range_end')
            self.codeinput.mark_set("range_start", "range_end")


if __name__ == "__main__":
    Interface()
