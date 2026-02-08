import ast
import builtins


class UndefinedVarDetector(ast.NodeVisitor):
    """
    Detect variables used before assignment
    """

    def __init__(self, tree):
        self.tree = tree
        # built-ins are considered already defined
        self.assigned = set(dir(builtins))
        self.assigned.add("__file__")
        self.used = []
        self.issues = []

    def run(self):
        self.visit(self.tree)

        for name, line in self.used:
            if name not in self.assigned:
                self.issues.append({
                    "type": "UndefinedVariable",
                    "message": f"Variable '{name}' used before assignment",
                    "line": line
                })

        return self.issues

    def visit_FunctionDef(self, node):
        # function name is defined
        self.assigned.add(node.name)

        # function parameters are defined
        for arg in node.args.args:
            self.assigned.add(arg.arg)

        self.generic_visit(node)

    def visit_ClassDef(self, node):
        self.assigned.add(node.name)
        self.generic_visit(node)

    def visit_Assign(self, node):
        for t in node.targets:
            if isinstance(t, ast.Name):
                self.assigned.add(t.id)
        self.generic_visit(node)

    def visit_Import(self, node):
        for alias in node.names:
            self.assigned.add(alias.asname or alias.name)
        self.generic_visit(node)

    def visit_ImportFrom(self, node):
        for alias in node.names:
            self.assigned.add(alias.asname or alias.name)
        self.generic_visit(node)

    def visit_For(self, node):
        # Handle: for x in ...
        if isinstance(node.target, ast.Name):
            self.assigned.add(node.target.id)

        # Handle: for k, v in ...
        elif isinstance(node.target, (ast.Tuple, ast.List)):
            for elt in node.target.elts:
                if isinstance(elt, ast.Name):
                    self.assigned.add(elt.id)

        # Visit body manually to ensure correct order
        for stmt in node.body:
            self.visit(stmt)

        for stmt in node.orelse:
            self.visit(stmt)

    def visit_With(self, node):
        # with open(...) as f:
        for item in node.items:
            if item.optional_vars and isinstance(item.optional_vars, ast.Name):
                self.assigned.add(item.optional_vars.id)
        self.generic_visit(node)

    def visit_ExceptHandler(self, node):
        # except Exception as e:
        if node.name:
            if isinstance(node.name, str):
                self.assigned.add(node.name)
            elif isinstance(node.name, ast.Name):
                self.assigned.add(node.name.id)
        self.generic_visit(node)

    def visit_Name(self, node):
        if isinstance(node.ctx, ast.Load):
            self.used.append((node.id, node.lineno))
        self.generic_visit(node)

