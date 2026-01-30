import ast
import builtins

SAFE_BUILTINS = set(dir(builtins))

class UndefinedVarDetector(ast.NodeVisitor):
    def __init__(self, tree):
        self.tree = tree
        self.issues = []
        self.scopes = [{}]

    def run(self):
        self.visit(self.tree)
        return self.issues

    def _push_scope(self):
        self.scopes.append({})

    def _pop_scope(self):
        self.scopes.pop()

    def _define_var(self, name):
        self.scopes[-1][name] = True

    def _is_defined(self, name):
        for scope in reversed(self.scopes):
            if name in scope:
                return True
        return False

    def visit_FunctionDef(self, node):
        self._define_var(node.name)
        self._push_scope()
        for arg in node.args.args:
            self._define_var(arg.arg)
        self.generic_visit(node)
        self._pop_scope()

    def visit_Assign(self, node):
        for target in node.targets:
            if isinstance(target, ast.Name):
                self._define_var(target.id)
        self.generic_visit(node)

    def visit_Name(self, node):
        if isinstance(node.ctx, ast.Load):
            if not self._is_defined(node.id) and node.id not in SAFE_BUILTINS:
                self.issues.append({
                    "type": "UndefinedVariable",
                    "message": f"Variable '{node.id}' used before assignment",
                    "line": node.lineno
                })
        self.generic_visit(node)
