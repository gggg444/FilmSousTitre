from __future__ import annotations

"""src/utils/config.py
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Centralised configuration loader.

Reads key–value pairs from ``config/config.yaml`` (YAML syntax) once and
caches the result for fast, repeated access. Supports dotted‑path lookup
for nested fields, e.g. ``get_config("audio.preferredcodec")``.

Example
-------
```python
from src.utils.config import get_config

ffmpeg = get_config("ffmpeg_path")
quality = get_config("audio.preferredquality", 192)
```
"""

from pathlib import Path
from typing import Any, Dict, Optional

import yaml

__all__ = ["load_config", "get_config"]

# ---------------------------------------------------------------------------
# Private cache so we only hit the disk once per interpreter session
# ---------------------------------------------------------------------------
_config_cache: Optional[Dict[str, Any]] = None


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def load_config(config_path: str | Path = "config/config.yaml") -> Dict[str, Any]:
    """Load YAML config file and cache the dictionary globally."""
    global _config_cache

    if _config_cache is not None:
        return _config_cache

    cfg_path = Path(config_path).expanduser()
    if not cfg_path.exists():
        raise FileNotFoundError(
            f"Configuration file not found: {cfg_path}. "
            "Create it or specify a custom path."
        )

    with cfg_path.open("r", encoding="utf-8") as fp:
        _config_cache = yaml.safe_load(fp) or {}

    return _config_cache


def get_config(key: str, default: Any | None = None, *, _config: Dict[str, Any] | None = None) -> Any:
    """Retrieve a value from the loaded config using dotted‑path notation.

    Parameters
    ----------
    key : str
        Dotted key path, e.g. ``"audio.preferredcodec"``.
    default : Any, optional
        Fallback value if key is missing.

    Returns
    -------
    Any
        The requested configuration value (or *default*).
    """

    if _config is None:
        _config = load_config()

    node: Any = _config
    for part in key.split("."):
        if isinstance(node, dict) and part in node:
            node = node[part]
        else:
            return default
    return node


# ---------------------------------------------------------------------------
# CLI usage: ``python -m src.utils.config ffmpeg_path``
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Print a value from config.yaml")
    parser.add_argument("key", help="Dotted key path, e.g. audio.preferredcodec")
    parser.add_argument("--default", help="Default if key is missing", default=None)
    parser.add_argument(
        "--config", help="Path to custom config file", default="config/config.yaml"
    )
    args = parser.parse_args()

    try:
        value = get_config(args.key, default=args.default, _config=load_config(args.config))
        print(value)
    except Exception as exc:
        parser.error(str(exc))
