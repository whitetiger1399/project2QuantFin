"""Consistent progress reporting for interactive and batch commands."""

from __future__ import annotations

from collections.abc import Iterable, Iterator
from typing import TypeVar

from tqdm.auto import tqdm


T = TypeVar("T")


def progress(
    values: Iterable[T],
    *,
    description: str,
    total: int | None = None,
    unit: str = "item",
) -> Iterator[T]:
    """Progress bar with elapsed time, rate, percentage, and ETA."""
    return iter(
        tqdm(
            values,
            desc=description,
            total=total,
            unit=unit,
            dynamic_ncols=True,
            mininterval=1.0,
            smoothing=0.1,
            bar_format=(
                "{desc}: {percentage:3.0f}%|{bar}| {n_fmt}/{total_fmt} "
                "[{elapsed}<{remaining}, {rate_fmt}]"
            ),
        )
    )

