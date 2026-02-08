from core.analyzer import Analyzer

sample_code = """
x = 10
y = 0
print(z)  # undefined variable
x = 5    # duplicate assignment
while True:
    print(x / y)
def func(a, b, c, d, e, f, g):
    pass
unused_var = 100
"""

analyzer = Analyzer(sample_code)
results = analyzer.analyze()

print("Detected Issues:")
for issue in results:
    print(issue)
