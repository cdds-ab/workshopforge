"""
Utility functions for WorkshopForge.

Provides common operations for file handling, path resolution,
and data processing.
"""

import hashlib
import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List


def ensure_dir(path: Path) -> Path:
    """
    Ensure directory exists, create if necessary.

    Args:
        path: Directory path to create

    Returns:
        The created/existing directory path
    """
    path.mkdir(parents=True, exist_ok=True)
    return path


def read_yaml(path: Path) -> Dict[str, Any]:
    """
    Read and parse YAML file.

    Args:
        path: Path to YAML file

    Returns:
        Parsed YAML data as dictionary

    Raises:
        FileNotFoundError: If file doesn't exist
        yaml.YAMLError: If YAML is invalid
    """
    import yaml

    if not path.exists():
        raise FileNotFoundError(f"YAML file not found: {path}")

    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def write_yaml(path: Path, data: Dict[str, Any]) -> None:
    """
    Write data to YAML file with consistent formatting.

    Args:
        path: Output file path
        data: Data to serialize
    """
    import yaml

    ensure_dir(path.parent)
    with open(path, "w", encoding="utf-8") as f:
        yaml.dump(data, f, default_flow_style=False, sort_keys=True, allow_unicode=True)


def read_json(path: Path) -> Dict[str, Any]:
    """
    Read and parse JSON file.

    Args:
        path: Path to JSON file

    Returns:
        Parsed JSON data

    Raises:
        FileNotFoundError: If file doesn't exist
        json.JSONDecodeError: If JSON is invalid
    """
    if not path.exists():
        raise FileNotFoundError(f"JSON file not found: {path}")

    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def write_json(path: Path, data: Any, indent: int = 2) -> None:
    """
    Write data to JSON file with consistent formatting.

    Args:
        path: Output file path
        data: Data to serialize
        indent: Indentation level for pretty-printing
    """
    ensure_dir(path.parent)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=indent, sort_keys=True, ensure_ascii=False)


def compute_hash(content: str) -> str:
    """
    Compute SHA-256 hash of content.

    Args:
        content: String content to hash

    Returns:
        Hexadecimal hash digest (first 16 chars)
    """
    return hashlib.sha256(content.encode("utf-8")).hexdigest()[:16]


def timestamp() -> str:
    """
    Get current timestamp in ISO format.

    Returns:
        ISO formatted timestamp string
    """
    return datetime.utcnow().isoformat() + "Z"


def sorted_dict_keys(d: Dict[str, Any]) -> List[str]:
    """
    Get sorted dictionary keys for deterministic traversal.

    Args:
        d: Dictionary to extract keys from

    Returns:
        Sorted list of keys
    """
    return sorted(d.keys())


def safe_filename(s: str) -> str:
    """
    Convert string to safe filename (lowercase, alphanumeric, dashes).

    Args:
        s: Input string

    Returns:
        Sanitized filename string
    """
    import re

    # Convert to lowercase and replace spaces/underscores with dashes
    s = s.lower().replace(" ", "-").replace("_", "-")
    # Remove non-alphanumeric except dashes
    s = re.sub(r"[^a-z0-9-]", "", s)
    # Collapse multiple dashes
    s = re.sub(r"-+", "-", s)
    return s.strip("-")


def find_spec_dir(start_path: Path) -> Path:
    """
    Find spec directory by walking up from start path.

    Args:
        start_path: Starting directory to search from

    Returns:
        Path to spec directory

    Raises:
        FileNotFoundError: If no spec directory found
    """
    current = start_path.resolve()
    while current != current.parent:
        spec_dir = current / "spec"
        if spec_dir.is_dir():
            return spec_dir
        current = current.parent

    raise FileNotFoundError(f"No spec/ directory found from {start_path}")


def relative_to_base(path: Path, base: Path) -> str:
    """
    Get path relative to base, or absolute if not relative.

    Args:
        path: Path to make relative
        base: Base path

    Returns:
        String representation of relative path
    """
    try:
        return str(path.relative_to(base))
    except ValueError:
        return str(path)
