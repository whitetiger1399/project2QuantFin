"""Expected pipeline errors that should be shown without Python tracebacks."""

from __future__ import annotations

from pathlib import Path


class QuantFinError(Exception):
    """Base class for expected, user-actionable pipeline failures."""


class SourceFetchError(QuantFinError):
    def __init__(self, source: str, failure_record: Path, cause: BaseException) -> None:
        self.source = source
        self.failure_record = failure_record
        self.cause = cause
        super().__init__(
            f"{source} fetch failed: {cause}\nFailure details: {failure_record}"
        )

