"""
Specification validator using JSON Schema.

Validates workshop specifications against JSON schemas to ensure
correctness and completeness before generation.
"""

from pathlib import Path
from typing import Any, Dict, List

from jsonschema import Draft7Validator

from .utils import read_json, read_yaml


class ValidationError(Exception):
    """Raised when spec validation fails."""

    pass


class SpecValidator:
    """
    Validates workshop specifications against JSON schemas.

    Loads schemas from schemas/ directory and validates YAML specs
    against them, providing detailed error messages.
    """

    def __init__(self, schema_dir: Path):
        """
        Initialize validator with schema directory.

        Args:
            schema_dir: Path to directory containing JSON schema files

        Raises:
            FileNotFoundError: If schema_dir doesn't exist
        """
        if not schema_dir.exists():
            raise FileNotFoundError(f"Schema directory not found: {schema_dir}")

        self.schema_dir = schema_dir.resolve()
        self._schemas: Dict[str, Any] = {}

    def load_schemas(self) -> None:
        """
        Load all JSON schemas from schema directory.

        Raises:
            json.JSONDecodeError: If schema files are invalid JSON
        """
        schema_files = {
            "workshop": "workshop.schema.json",
            "modules": "modules.schema.json",
            "profile": "profile.schema.json",
        }

        for name, filename in schema_files.items():
            schema_path = self.schema_dir / filename
            if not schema_path.exists():
                raise FileNotFoundError(f"Required schema missing: {schema_path}")
            self._schemas[name] = read_json(schema_path)

    def validate_spec(self, spec_name: str, spec_data: Dict[str, Any]) -> List[str]:
        """
        Validate a specification against its schema.

        Args:
            spec_name: Name of spec (workshop, modules, profile)
            spec_data: Specification data to validate

        Returns:
            List of validation error messages (empty if valid)

        Raises:
            KeyError: If schema for spec_name not found
        """
        if not self._schemas:
            self.load_schemas()

        if spec_name not in self._schemas:
            raise KeyError(f"No schema found for spec: {spec_name}")

        schema = self._schemas[spec_name]
        validator = Draft7Validator(schema)

        errors = []
        for error in validator.iter_errors(spec_data):
            # Format error with path and message
            path = ".".join(str(p) for p in error.absolute_path) if error.absolute_path else "root"
            errors.append(f"[{spec_name}] {path}: {error.message}")

        return errors

    def validate_file(self, spec_file: Path) -> List[str]:
        """
        Validate a single spec file.

        Args:
            spec_file: Path to YAML spec file

        Returns:
            List of validation errors (empty if valid)
        """
        # Determine spec type from filename
        spec_name = spec_file.stem  # workshop, modules, profile
        if spec_name not in ["workshop", "modules", "profile"]:
            return [f"Unknown spec type: {spec_name}"]

        try:
            spec_data = read_yaml(spec_file)
            return self.validate_spec(spec_name, spec_data)
        except Exception as e:
            return [f"Failed to load {spec_file}: {e}"]

    def validate_directory(self, spec_dir: Path) -> Dict[str, List[str]]:
        """
        Validate all specs in a directory.

        Args:
            spec_dir: Path to spec directory

        Returns:
            Dictionary mapping spec names to lists of errors
        """
        results = {}

        for spec_name in ["workshop", "modules", "profile"]:
            spec_file = spec_dir / f"{spec_name}.yml"
            if spec_file.exists():
                errors = self.validate_file(spec_file)
                if errors:
                    results[spec_name] = errors
            else:
                # Only workshop and modules are required
                if spec_name in ["workshop", "modules"]:
                    results[spec_name] = [f"Required file missing: {spec_file}"]

        return results

    def is_valid(self, spec_dir: Path) -> bool:
        """
        Check if all specs in directory are valid.

        Args:
            spec_dir: Path to spec directory

        Returns:
            True if all specs are valid, False otherwise
        """
        results = self.validate_directory(spec_dir)
        return len(results) == 0
