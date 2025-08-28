import sys, pathlib
# Ensure src/ is on path for package imports (explicit fallback tweak)
root = pathlib.Path(__file__).resolve().parents[1]
# After moving packages to repo root, ensure repository root is on sys.path
if str(root) not in sys.path:
    sys.path.insert(0, str(root))
