# version.py
import os
import sys


APP_VERSION = "1.0.0"

# Try to read from file for development
def _try_read_version():
    try:
        if not getattr(sys, 'frozen', False):
            # Only try to read file when running as script
            version_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "version.txt")
            if os.path.exists(version_file):
                with open(version_file, "r", encoding="utf-8") as f:
                    return f.read().strip()
    except:
        pass
    return APP_VERSION

# Override if file exists (only in development)
if not getattr(sys, 'frozen', False):
    APP_VERSION = _try_read_version()