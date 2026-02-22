# T00_0_check_imports.py -- check that dev deps are good

packages = [
    ("PySide6",   "PySide6",   "__version__"),
    ("PyQtGraph", "pyqtgraph", "__version__"),
    ("docker",    "docker",    "__version__"),
    ("numpy",     "numpy",     "__version__"),
]

for name, module, ver_attr in packages:
    try:
        mod = __import__(module)
        ver = getattr(mod, ver_attr, "?")
        print(f"  OK  {name} ({ver})")
    except ImportError as e:
        print(f"  FAIL {name}: {e}")

try:
    import yoda
    print(f"  OK  yoda ({getattr(yoda, '__version__', '?')})")
except ImportError:
    print("  --  yoda: not installed")

try:
    import config
    print(f"  OK  config (ROOT={config.ROOT})")
except Exception as e:
    print(f"  FAIL config: {e}")
