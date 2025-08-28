import sys, pathlib
# Ensure src/ is on path for package imports (explicit fallback tweak)
root = pathlib.Path(__file__).resolve().parents[1]
src = root / 'src'
if str(src) not in sys.path:
    sys.path.insert(0, str(src))
