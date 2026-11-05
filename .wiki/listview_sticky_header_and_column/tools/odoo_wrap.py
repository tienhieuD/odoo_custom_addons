import os, sys, runpy
sys.path.insert(0, os.getcwd())
import odoo.tests.common as common
if hasattr(common, "_find_executable"):
    common._find_executable = lambda: os.environ["ODOO_BROWSER_BIN"]
if hasattr(common, "ChromeBrowser"):
    common.ChromeBrowser.executable = property(lambda self: os.environ["ODOO_BROWSER_BIN"])
if os.environ.get("WRAP_PORT") and hasattr(common, "PORT"):
    common.PORT = int(os.environ["WRAP_PORT"])
sys.argv = ["odoo-bin"] + sys.argv[1:]
runpy.run_path("odoo-bin", run_name="__main__")
