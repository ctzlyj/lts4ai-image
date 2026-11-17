#!/usr/bin/env python3
"""Compatibility entry point; new installs use lts4ai_image.py."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from lts4ai_image import *  # noqa: F401,F403

if __name__ == "__main__":
    raise SystemExit(main())
