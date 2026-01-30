from .fix_agent import FixAgent

def apply_all_fixes(original_code, issues):
    """
    Takes the raw code and a list of issues, applies fixes line-by-line,
    and returns the updated code and a log of what was changed.
    """
    # 1. Split the code into a list of lines
    lines = original_code.splitlines()
    agent = FixAgent()
    fix_log = []

    # 2. IMPORTANT: Sort issues by line number in REVERSE order (bottom to top).
    # This ensures that if we change a line, it doesn't shift the line numbers 
    # for the errors appearing later in the file.
    sorted_issues = sorted(issues, key=lambda x: x['line'], reverse=True)

    for issue in sorted_issues:
        line_number = issue['line']
        error_id = issue['id']
        
        # Line numbers are 1-based, but Python lists are 0-based
        idx = line_number - 1
        
        if 0 <= idx < len(lines):
            original_line = lines[idx]
            fixed_line = agent.fix_line(original_line, error_id)
            
            # Only update if a fix was actually applied
            if fixed_line != original_line:
                lines[idx] = fixed_line
                fix_log.append(f"Fixed Line {line_number}: Applied {error_id}")
            else:
                fix_log.append(f"Skipped Line {line_number}: No rule found for {error_id}")

    # 3. Join the lines back into a single string
    fixed_code = "\n".join(lines)
    
    return fixed_code, fix_log