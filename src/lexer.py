from pygments.lexer import RegexLexer, words
from pygments.token import Comment, Keyword, Number, Text, String

from compiler.parser import KEYWORDS, TYPES


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


if __name__ == '__main__':
    code = 'алг\nнач\n  цел а := 1+2\nкон'

    # highlight(code, KuMirLexer(), GifImageFormatter(), outfile='out.gif')
    lexer = KuMirLexer()
    for start, token, text in lexer.get_tokens_unprocessed(code):
        print(start, start + len(text), token)
