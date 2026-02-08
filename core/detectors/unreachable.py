import ast

class UnreachableCodeDetector(ast.NodeVisitor):
    """
    Detect code after return, break, or raise
    """
    def __init__(self, tree):
        self.tree = tree
        self.issues = []
        self.dead = False

    def run(self):
        self.visit(self.tree)
        return self.issues

    def visit_FunctionDef(self, node):
        self.dead = False
        self.generic_visit(node)

    def visit_Return(self, node):
        self.dead = True
        self.generic_visit(node)

    def visit_Raise(self, node):
        self.dead = True
        self.generic_visit(node)

    def visit_Expr(self, node):
        if self.dead:
            self.issues.append({
                "type": "UnreachableCode",
                "message": "This statement will never execute",
                "line": node.lineno
            })
        self.generic_visit(node)
