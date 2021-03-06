class CallEvalPrinter:
    def __init__(self, expr):
        self.expr = expr

    def print(self):
        return self.expr.accept(self)

    def visitCallTerm(self, term):
        args = ", ".join([arg.accept(self) for arg in term.args])
        return term.callee + "(" + args + ")"

    def visitGroupingExpr(self, expr):
        return expr.expression.accept(self)

    def visitBinaryExpr(self, expr):
        return (
            str(expr.left.accept(self))
            + " "
            + str(expr.operator.lexeme)
            + " "
            + str(expr.right.accept(self))
        )

    def visitUnaryExpr(self, expr):
        return str(expr.operator.lexeme) + " " + str(expr.right.accept(self))

    def visitCallExpr(self, expr):
        args = ", ".join([arg.accept(self) for arg in expr.args])
        return expr.callee.name.lexeme + "(" + args + ")"

    def visitVariableExpr(self, expr):
        return "__DATA__['" + expr.name.lexeme + "']"

    def visitLiteralExpr(self, expr):
        return expr.value

    def visitQuotedNameExpr(self, expr):
        # delete backquotes in 'variable'
        return "__DATA__['" + expr.expression.lexeme[1:-1] + "']"


class CallNamePrinter(CallEvalPrinter):
    def visitVariableExpr(self, expr):
        return expr.name.lexeme

    def visitQuotedNameExpr(self, expr):
        return expr.expression.lexeme
