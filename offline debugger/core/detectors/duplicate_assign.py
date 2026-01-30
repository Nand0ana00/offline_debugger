import ast

class DuplicateAssignDetector(ast.NodeVisitor):
    """
    Detect variables assigned multiple times in the same scope
    """
    def __init__(self, tree):
        self.tree = tree
        self.issues = []
        self.assigned = [{}]  # stack of scopes

    def run(self):
        self.visit(self.tree)
        return self.issues

    def _push_scope(self):
        self.assigned.append({})

    def _pop_scope(self):
        self.assigned.pop()

    def visit_FunctionDef(self, node):
        self._push_scope()
        self.generic_visit(node)
        self._pop_scope()

    def visit_Assign(self, node):
        scope = self.assigned[-1]
        for t in node.targets:
            if isinstance(t, ast.Name):
                if t.id in scope:
                    self.issues.append({
                        "type": "DuplicateAssignment",
                        "message": f"Variable '{t.id}' assigned multiple times",
                        "line": node.lineno
                    })
                scope[t.id] = node.lineno
        self.generic_visit(node)
