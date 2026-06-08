from __future__ import annotations

import time
from collections.abc import Callable


def translate_with_retry(
    action: Callable[[], str],
    *,
    attempts: int = 3,
    base_delay: float = 1.5,
) -> str:
    last_error: Exception | None = None

    for attempt in range(attempts):
        try:
            return action()
        except Exception as exc:
            last_error = exc
            message = str(exc).casefold()
            retryable = any(
                token in message
                for token in ("504", "502", "503", "429", "timeout", "timed out")
            )
            if not retryable or attempt >= attempts - 1:
                raise
            time.sleep(base_delay * (attempt + 1))

    if last_error is not None:
        raise last_error
    raise RuntimeError("Traduction impossible")
