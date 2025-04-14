from pygments import highlight
from pygments.formatters import HtmlFormatter
from pygments.lexer import RegexLexer, words
from pygments.token import Comment, Keyword, Number, Text, String

from compiler.constants import KEYWORDS, TYPES

CSS = '''<style>
.k {
    color: red;
}
.s {
    color: orange;
}
.c {
    color: grey;
}
</style>'''
# self.codeinput.tag_configure("Token.Literal.String", foreground='orange')
# self.codeinput.tag_configure("Token.Comment", foreground="grey")


class KuMirLexer(RegexLexer):
    name = 'KuMir'

    tokens = {
        'root': [
            (words(TYPES, suffix=r'\b'), Keyword),
            (words(KEYWORDS, suffix=r'\b'), Keyword),
            (r'".*"', String),
            (r'\b\d+', Number),
            (r'\w+', Text),
            (r'\s+', Text),
            (r'\|.*', Comment),
        ]
    }


def highlight_text(text: str) -> str:
    return f'{CSS}<pre>{highlight(text, KuMirLexer(), HtmlFormatter(lineseparator='<br />'))[:-1]}</pre>'


if __name__ == '__main__':
    code = 'алг\nнач\n  цел а := 1+2\nкон'

    print(repr(highlight_text(code)))
    # lexer = KuMirLexer()
    # for start, token, text in lexer.get_tokens_unprocessed(code):
    #     print(start, start + len(text), token)
