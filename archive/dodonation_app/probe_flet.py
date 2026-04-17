import inspect
import sys

try:
    import flet

    print("flet loaded:", flet)
    print("version:", getattr(flet, "__version__", "unknown"))

    print("has WEB_BROWSER:", hasattr(flet, "WEB_BROWSER"))
    print("has WEB_PAGE:", hasattr(flet, "WEB_PAGE"))
    print("has WEBVIEW:", hasattr(flet, "WEBVIEW"))
    print("has VIEW:", hasattr(flet, "VIEW"))

    print(
        "module dir sample:",
        [a for a in dir(flet) if "WEB" in a or "BROWSER" in a or "view" in a.lower()][:40],
    )

    print("run attr exists:", hasattr(flet, "run"))
    print("app attr exists:", hasattr(flet, "app"))

    if hasattr(flet, "app"):
        print("app signature:", inspect.signature(flet.app))

    if hasattr(flet, "run"):
        print("run signature:", inspect.signature(flet.run))

    print("flet file:", getattr(flet, "__file__", None))

except Exception as e:
    print("error:", repr(e))
    sys.exit(1)