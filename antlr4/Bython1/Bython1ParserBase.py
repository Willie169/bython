from antlr4 import *

class Bython1ParserBase(Parser):

    def CannotBePlusMinus(self) -> bool:
        return True

    def CannotBeDotLpEq(self) -> bool:
        return True
