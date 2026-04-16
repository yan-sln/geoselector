# -*- coding: utf-8 -*-
"""Utility to decide which search operation should be used.

The logic mirrors the previous heuristic that lived in ``core.selector`` but
is now isolated so it can be unit‑tested independently and extended without
touching the selector implementation.
"""

from __future__ import annotations

from typing import Any, Tuple


class OperationSelector:
    """Choose the appropriate operation name based on the call arguments.

    The method receives the raw ``args`` tuple passed to ``SelectorImpl.select``
    and the entity configuration dictionary extracted from ``apis.json``.
    It returns one of the operation keys that exist in the configuration:
    ``search_by_name``, ``search_by_code``, ``list_search`` or ``search``.
    """

    @staticmethod
    def choose(args: Tuple[Any, ...], cfg: dict[str, Any]) -> str:
        """Select the appropriate operation key from the entity configuration.

        Parameters
        ----------
        args: Tuple[Any, ...]
            The raw arguments tuple passed to ``SelectorImpl.select``.
        cfg: dict[str, Any]
            The configuration dictionary for the entity extracted from ``apis.json``.

        Returns
        -------
        str
            The operation key that should be used for the request. It will be one
            of the keys present in ``cfg`` such as ``search_by_name``,
            ``search_by_code``, ``list_search`` or ``search``.

        Notes
        -----
        The method implements a heuristic:

        * If a single ``dict`` argument is provided, it is treated as filters for a
          list‑search‑like operation.
        * If a single ``str`` argument is provided, the method decides between a
          name‑based or code‑based search based on the content of the string.
        * Otherwise positional arguments are mapped to a list‑search‑like
          operation.
        """
        # 1⃣ Dict argument – treat as filters for a list‑search‑like operation.
        if args and isinstance(args[0], dict) and len(args) == 1:
            for key in cfg.keys():
                if key.startswith("list_search"):
                    return key
            return "search" if "search" in cfg else next(iter(cfg))

        # 2⃣ Single string – decide via heuristic (code vs name).
        if args and isinstance(args[0], str) and len(args) == 1:
            text = args[0]
            if "search_by_name" in cfg and "search_by_code" in cfg:
                return (
                    "search_by_code"
                    if text.isdigit()
                    else "search_by_name"
                )
            if "search_by_code" in cfg:
                return "search_by_code"
            if "search_by_name" in cfg:
                return "search_by_name"
            if "search" in cfg:
                return "search"
            for key in cfg.keys():
                if key.startswith("list_search"):
                    return key
            return next(iter(cfg))

        # 3⃣ Positional arguments – map to a list‑search‑like operation.
        for key in cfg.keys():
            if key.startswith("list_search"):
                return key

        # Default fallback – generic ``search`` if present.
        return "search" if "search" in cfg else next(iter(cfg))
