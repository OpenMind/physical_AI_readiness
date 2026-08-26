"""Find a Chromium-family browser to render the PDFs with.

The build runs in three places — a Linux container, a Mac, a Linux desktop —
and each keeps Chrome somewhere different. Rather than hard-code one path,
look in all the usual ones and let $CHROME override.
"""
import os, pathlib, shutil

CANDIDATES = [
    # this container
    "/opt/pw-browsers/chromium-1194/chrome-linux/chrome",
    # macOS
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    "/Applications/Chromium.app/Contents/MacOS/Chromium",
    "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge",
    "/Applications/Brave Browser.app/Contents/MacOS/Brave Browser",
    # Linux
    "/usr/bin/google-chrome", "/usr/bin/google-chrome-stable",
    "/usr/bin/chromium", "/usr/bin/chromium-browser",
    "/snap/bin/chromium",
]
NAMES = ["google-chrome", "google-chrome-stable", "chromium",
         "chromium-browser", "chrome", "microsoft-edge"]


def find():
    """Path to a usable browser, or None. $CHROME wins if it is set."""
    env = os.environ.get("CHROME")
    if env and pathlib.Path(env).exists():
        return env
    for p in CANDIDATES:
        if pathlib.Path(p).exists():
            return p
    for n in NAMES:
        p = shutil.which(n)
        if p:
            return p
    return None


HINT = ("No Chrome or Chromium found. Install Google Chrome, or point the build "
        "at an existing copy:\n    CHROME='/path/to/chrome' python3 src/build.py report")
