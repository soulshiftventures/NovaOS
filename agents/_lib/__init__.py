import importlib as _im
try:
    telemetry = _im.import_module("lib.telemetry")
except ModuleNotFoundError:
    # last resort: allow running directly from this folder, if someone later puts telemetry here
    try:
        telemetry = _im.import_module("agents._lib.telemetry")
    except Exception as e:
        raise
