from sa7k38 import CodeValidator

# =======================
# TEST CASES
# =======================

tests = [
    {
        "name": "Valid code",
        "original": "x = 10\ny = 20\nprint(x + y)",
        "fixed": "x = 10\ny = 20\nprint(x + y)",
    },
    {
        "name": "Syntax error",
        "original": "x = 1",
        "fixed": "if x == 1 print(x)",  # missing colon
    },
    {
        "name": "Security violation",
        "original": "x = 2",
        "fixed": "eval('2+2')",
    },
    {
        "name": "Infinite loop",
        "original": "",
        "fixed": "while True: pass",
    },
    {
        "name": "Bare except",
        "original": "",
        "fixed": "try:\n    x=1\nexcept:\n    pass",
    },
    {
        "name": "Structural regression",
        "original": "x=1\ny=2\nz=3\nprint(x+y+z)",
        "fixed": "x=1\nprint(x)",
    },
]

# =======================
# RUN TESTS
# =======================

for test in tests:
    print(f"\n=== Test: {test['name']} ===")
    validator = CodeValidator(test["original"], test["fixed"])
    result = validator.validate()

    print("Status:", result.status)
    print("Trust Score:", result.trust_score)
    print("Risk Level:", result.risk_level)
    print("Readiness:", result.readiness)
    print("Errors:", result.errors)
    print("Warnings:", result.warnings)
    print("Metrics:", result.metrics)