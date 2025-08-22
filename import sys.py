import sys
print("Executable:", sys.executable)
print("Paths:")
for p in sys.path:
    print("  ", p)


