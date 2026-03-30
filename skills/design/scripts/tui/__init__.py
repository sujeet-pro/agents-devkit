"""DevKit TUI Framework — Textual-based interactive components for skill workflows."""
import subprocess
import sys

try:
    import textual  # noqa: F401
except ImportError:
    print("First run — installing textual...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-q", "textual>=1.0.0"])
    except Exception:
        print("Failed. Please run manually: pip install 'textual>=1.0.0'")
        sys.exit(1)
    print("Done.")

from .base import DevKitApp, EditModal, ICONS, load_json, save_json  # noqa: F401
