from typing import TextIO
from antlr4 import *
from antlr4.Token import CommonToken
from Bython1Parser import Bython1Parser;

import sys
from typing import TextIO
import re


class Bython1LexerBase(Lexer):
    NEW_LINE_PATTERN = re.compile('[^\r\n\f]+')
    SPACES_PATTERN = re.compile('[\r\n\f]+')

    def __init__(self, input: InputStream, output: TextIO = sys.stdout):
        super().__init__(input, output)
        self.tokens = []
        self.indents = []
        self.opened = 0
    
    def reset(self):
        self.tokens = []
        self.opened = 0
        super().reset()
    
    def emitToken(self, token):
        self._token = token
        self.tokens.append(token)
    
    def nextToken(self):
        if self._input.LA(1) == Python3Parser.EOF:
            self.tokens = [token for token in self.tokens if token.type != Python3Parser.EOF]
            self.emitToken(self.commonToken(Python3Parser.NEWLINE, '\n'))
            self.emitToken(self.commonToken(Python3Parser.EOF, '<EOF>'))

        next_ = super().nextToken()
        return next_ if len(self.tokens) == 0 else self.tokens.pop(0)

    def commonToken(self, type_: int, text: str):
        stop = self.getCharIndex() - 1
        start = stop if text == '' else stop - len(text) + 1
        return CommonToken(self._tokenFactorySourcePair, type_, Lexer.DEFAULT_TOKEN_CHANNEL, start, stop)

    def atStartOfInput(self):
        return self.getCharIndex() == 0

    def openBrace(self):
        self.opened += 1

    def closeBrace(self):
        self.opened -= 1

    def onNewLine(self):
        new_line = self.NEW_LINE_PATTERN.sub('', self.text)
        spaces = self.SPACES_PATTERN.sub('', self.text)
        next_ = self._input.LA(1)
        next_next = self._input.LA(2)

        if self.opened > 0 or (next_next != -1 and next_ in (10, 13, 35)):
            self.skip()
        else:
            self.emitToken(self.commonToken(Bython1Parser.NEWLINE, new_line))
