import ast

class UnusedVarDetector(ast.NodeVisitor):
    """
    Detect variables that are assigned but never used
    """
    def __init__(self, tree):
        self.tree = tree
        self.assigned = {}
        self.used = set()
        self.issues = []

    def run(self):
        self.visit(self.tree)
        for var, line in self.assigned.items():
            if var not in self.used:
                self.issues.append({
                    "type": "UnusedVariable",
                    "message": f"Variable '{var}' assigned but never used",
                    "line": line
                })
        return self.issues

    def visit_Assign(self, node):
        for t in node.targets:
            if isinstance(t, ast.Name):
                self.assigned[t.id] = node.lineno
        self.generic_visit(node)

    def visit_Name(self, node):
        if isinstance(node.ctx, ast.Load):
            self.used.add(node.id)
        self.generic_visit(node)
