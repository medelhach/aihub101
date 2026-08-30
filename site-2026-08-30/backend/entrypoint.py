"""Container start: apply migrations, then serve the API."""

from __future__ import annotations

import os
import subprocess
import sys


def main() -> None:
    subprocess.check_call([sys.executable, "-m", "alembic", "upgrade", "head"])
    os.execvp(
        sys.executable,
        [
            sys.executable,
            "-m",
            "uvicorn",
            "app.main:app",
            "--host",
            "0.0.0.0",
            "--port",
            "8000",
        ],
    )


if __name__ == "__main__":
    main()
