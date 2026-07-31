"""Launches the internal database admin GUI (.devtools/db_admin).

`.devtools` is not a valid Python package-name segment (leading dot), so this
script adds it to sys.path by filesystem path instead of relying on
`python -m devtools.db_admin` dotted-module resolution.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / ".devtools"))

from db_admin.app import main  # noqa: E402

if __name__ == "__main__":
    main()
