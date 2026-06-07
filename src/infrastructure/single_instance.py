from __future__ import annotations

import socket
import sys


def ensure_single_instance(port: int = 47293) -> bool:
    """Return False if another Diablo Translator instance is already running."""
    holder = getattr(ensure_single_instance, "_socket", None)
    if holder is not None:
        return True

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.bind(("127.0.0.1", port))
        sock.listen(1)
    except OSError:
        return False

    ensure_single_instance._socket = sock  # type: ignore[attr-defined]
    return True


def warn_if_already_running() -> bool:
    if ensure_single_instance():
        return False

    print(
        "Diablo Translator est deja ouvert.\n"
        "Fermez l'autre fenetre avant de relancer (sinon l'OCR ne fonctionne pas).",
        file=sys.stderr,
    )
    return True
