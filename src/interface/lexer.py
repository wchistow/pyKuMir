import os.path

from pygments import highlight
from pygments.formatters import HtmlFormatter
from pygments.lexer import RegexLexer, words
from pygments.token import Comment, Keyword, Number, Text, String

from interpreter.constants import KEYWORDS, TYPES

with open(os.path.join(os.path.dirname(__file__), 'code_style.css')) as f:
    CSS = f'<style>\n{f.read()}\n</style>'


class KuMirLexer(RegexLexer):
    name = 'KuMir'

    tokens = {
        'root': [
            (words(TYPES, suffix=r'\b'), Keyword.Type),
            (words(KEYWORDS, suffix=r'\b'), Keyword),
            (r'"[^"\n]*"', String),
            (r'\b\d+', Number),
            (r'\|.*', Comment),
        ]
    }


def highlight_text(text: str) -> str:
    return CSS + highlight_text_without_css(text)


def highlight_text_without_css(text: str) -> str:
    return f'<pre>{highlight(text, KuMirLexer(), HtmlFormatter(lineseparator="<br/>"))[:-1]}</pre>'

if __name__ == '__main__':
    code = 'алг\nнач\n  цел а := 1+2\nкон'

    print(repr(highlight_text(code)))
    # lexer = KuMirLexer()
    # for start, token, text in lexer.get_tokens_unprocessed(code):
    #     print(start, start + len(text), token)
