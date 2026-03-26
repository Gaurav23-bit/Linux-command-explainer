#!/usr/bin/env python3
"""
app.py - Entry point for Linux Command Explainer & Risk Detector
Run with: python app.py
"""

import sys
import os

# All files live in the same directory 
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)


def _check_python_version():
    if sys.version_info < (3, 10):
        print(
            f"[ERROR] Python 3.10 or newer is required.\n"
            f"        You are running Python {sys.version_info.major}.{sys.version_info.minor}.",
            file=sys.stderr,
        )
        sys.exit(1)


def _check_tkinter():
    try:
        import tkinter  # noqa: F401
    except ImportError:
        print(
            "[ERROR] Tkinter is not installed.\n"
            "        Debian/Ubuntu: sudo apt install python3-tk\n"
            "        Fedora/RHEL:   sudo dnf install python3-tkinter\n"
            "        Arch Linux:    sudo pacman -S tk",
            file=sys.stderr,
        )
        sys.exit(1)


def _check_data_files():
    required = ("commands.json", "flags.json", "risk_rules.json")
    missing = [f for f in required if not os.path.isfile(os.path.join(BASE_DIR, f))]
    if missing:
        print(
            f"[WARNING] Missing data files: {', '.join(missing)}\n"
            f"          Expected in: {BASE_DIR}",
            file=sys.stderr,
        )


def main():
    _check_python_version()
    _check_tkinter()
    _check_data_files()

    from interface import launch
    launch()


if __name__ == "__main__":
    main()
