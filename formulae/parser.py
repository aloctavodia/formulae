from .expr import Python, QuotedName, Grouping, Binary, Unary, Call, Variable, Literal
from .token import Token
from .utils import listify


class ParseError(Exception):
    pass


class Parser:
    """Consume sequences of Tokens"""

    def __init__(self, tokens):
        self.current = 0
        self.tokens = tokens
        # pass options to understand custom functionality

    def at_end(self):
        return self.peek().type == "EOF"

    def advance(self):
        if not self.at_end():
            self.current += 1
            return self.tokens[self.current - 1]

    def peek(self):
        """Returns the Token we are about to consume"""
        return self.tokens[self.current]

    def previous(self):
        """Returns the last Token we consumed"""
        return self.tokens[self.current - 1]

    def check(self, types):
        # Checks multiple types at once
        if self.at_end():
            return False
        return self.peek().type in listify(types)

    def match(self, types):
        if self.check(types):
            self.advance()
            return True
        else:
            return False

    def consume(self, _type, message):
        """Consumes the next Token

        First, it checks if the next Token is of the expected type.
        If True, it calls self.advance() and it's Saul Goodman.
        Otherwise, we've found an error.
        """
        if self.check(_type):
            return self.advance()
        else:
            raise ParseError(message)

    # Here we start walking through the grammar
    def parse(self):
        return self.expression()

    def expression(self):
        return self.tilde()

    def tilde(self):
        expr = self.random_effect()
        if self.match("TILDE"):
            operator = self.previous()
            right = self.addition()
            expr = Binary(expr, operator, right)
        return expr

    def random_effect(self):
        expr = self.addition()
        while self.match(["PIPE"]):
            operator = self.previous()
            right = self.addition()
            expr = Binary(expr, operator, right)
        return expr

    def addition(self):
        expr = self.multiplication()
        while self.match(["MINUS", "PLUS"]):
            operator = self.previous()
            right = self.multiplication()
            expr = Binary(expr, operator, right)
        return expr

    def multiplication(self):
        expr = self.interaction()
        while self.match(["STAR", "SLASH"]):
            operator = self.previous()
            right = self.interaction()
            expr = Binary(expr, operator, right)
        return expr

    def interaction(self):
        expr = self.multiple_interaction()
        while self.match(["COLON"]):
            operator = self.previous()
            right = self.multiple_interaction()
            expr = Binary(expr, operator, right)
        return expr

    def multiple_interaction(self):
        expr = self.unary()
        while self.match(["STAR_STAR"]):
            operator = self.previous()
            right = self.unary()
            expr = Binary(expr, operator, right)
        return expr

    def unary(self):
        if self.match(["PLUS", "MINUS"]):
            operator = self.previous()
            right = self.unary()
            return Unary(operator, right)
        return self.call()

    def call(self):
        expr = self.primary()
        while True:
            if self.match("LEFT_PAREN"):
                expr = self.finishcall(expr)
            else:
                break
        return expr

    def finishcall(self, expr):
        args = []
        if not self.check("RIGHT_PAREN"):
            while True:
                args.append(self.expression())
                if not self.match("COMMA"):
                    break
        self.consume("RIGHT_PAREN", "Expect ')' after arguments.")
        expr = Call(expr, args)
        return expr

    def primary(self):
        if self.match("NUMBER"):
            return Literal(self.previous().literal)
        elif self.match("IDENTIFIER"):
            identifier = self.previous()
            if self.match("LEFT_BRACKET"):
                level = self.expression()
                if not isinstance(level, Variable):
                    raise ValueError("Subset notation only allows a level name.")
                self.consume("RIGHT_BRACKET", "Expect ']' after level name.")
                return Variable(identifier, level)
            else:
                return Variable(self.previous())
        elif self.match("BQNAME"):
            return QuotedName(self.previous())
        elif self.match("LEFT_PAREN"):
            expr = self.expression()
            self.consume("RIGHT_PAREN", "Expect ')' after expression.")
            return Grouping(expr)
        elif self.match("LEFT_BRACE"):
            # {x + 1} is translated to I(x + 1) and then we resolve the latter.
            expr = self.expression()
            self.consume("RIGHT_BRACE", "Expect '}' after expression.")
            return Call(Variable(Token("IDENTIFIER", "I")), [expr])
        else:
            raise ParseError("Expect expression.")
