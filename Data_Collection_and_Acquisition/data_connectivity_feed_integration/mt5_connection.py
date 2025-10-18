# Guard MetaTrader5 import to avoid ModuleNotFoundError during CI/tests if MT5 is not installed.

try:
    import MetaTrader5 as mt5  # type: ignore
except Exception:
    mt5 = None  # code should check mt5 is not None before using it

# Helper wrappers to make usage safer in the rest of the module:

def mt5_initialize(*args, **kwargs):
    if mt5 is None:
        return False
    return mt5.initialize(*args, **kwargs)

def mt5_shutdown(*args, **kwargs):
    if mt5 is None:
        return True
    return mt5.shutdown(*args, **kwargs)

# When using mt5.* elsewhere, check mt5 is not None, e.g.:
# if not mt5_initialize(...):
#     raise RuntimeError("MetaTrader5 not available/initialized")
# ... then use mt5.* calls knowing mt5 is present.