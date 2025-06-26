import os.path

from pygments import highlight
from pygments.formatters import HtmlFormatter
from pygments.lexer import RegexLexer, words, bygroups
from pygments.token import Comment, Keyword, Number, String, Name, Whitespace, Punctuation

from interpreter.constants import KEYWORDS, TYPES

BOOLS = {'да', 'нет'}

with open(os.path.join(os.path.dirname(__file__), 'code_style.css'),
          encoding='utf-8') as f:
    CSS = f'<style>\n{f.read()}\n</style>'


class KuMirLexer(RegexLexer):
    name = 'KuMir'

    tokens = {
        'root': [
            (words(TYPES, prefix=r'\b', suffix=r'\b'), Keyword.Type),
            (words(KEYWORDS - BOOLS, prefix=r'\b', suffix=r'\b'), Keyword),
            (words(BOOLS, prefix=r'\b', suffix=r'\b'), Keyword.Constant),
            (
                r'(\w+)(\s*)(\()',
                bygroups(Name.Function, Whitespace, Punctuation)
            ),
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
    code = '''
    алг fib(арг цел n) нач
        вывод n
    кон'''

    print(repr(highlight_text(code)))
    # lexer = KuMirLexer()
    # for start, token, text in lexer.get_tokens_unprocessed(code):
    #     print(start, start + len(text), token)
