import json
import os
import re

class FixAgent:
    def __init__(self):
        # Load the rules database you created
        self.rules_path = os.path.join(os.path.dirname(__file__), 'fix_rules.json')
        self.rules = self._load_rules()

    def _load_rules(self):
        try:
            with open(self.rules_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return {}

    def fix_line(self, line_content, error_id):
        """
        Determines which strategy to use based on the error_id 
        and applies it to the provided line of code.
        """
        if error_id not in self.rules:
            return line_content # Return original if no rule exists

        rule = self.rules[error_id]
        action = rule['action']
        correction = rule['correction']

        # Dispatch to the correct internal method
        if action == "append_at_end":
            return self._append_at_end(line_content, correction)
        
        elif action == "add_indent":
            return self._add_indent(line_content, correction)
        
        elif action == "replace_operator":
            return self._replace_assignment_with_comparison(line_content)
        
        elif action == "wrap_content":
            return self._wrap_print(line_content)
        
        elif action == "comment_line":
            return self._comment_line(line_content, correction)

        return line_content

    # --- Specific Fix Strategies ---

    def _append_at_end(self, line, char):
        """Adds a character like : or ) to the end, preserving newline."""
        return line.rstrip() + char

    def _add_indent(self, line, whitespace):
        """Adds 4 spaces to the start of the line."""
        return whitespace + line

    def _replace_assignment_with_comparison(self, line):
        """Changes 'if x = 5' to 'if x == 5'"""
        if "if" in line and "=" in line and "==" not in line:
            return line.replace("=", "==")
        return line

    def _wrap_print(self, line):
        """Changes print 'hello' to print('hello')"""
        content = line.replace("print", "").strip()
        # Keep original indentation
        indent = re.match(r"\s*", line).group()
        return f"{indent}print({content})"

    def _comment_line(self, line, prefix):
        """Comments out a line (e.g., for unused imports)"""
        return prefix + line
    


   