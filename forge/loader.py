"""
Specification loader for WorkshopForge.

Discovers and loads workshop specifications from YAML files,
merging them into a unified data structure.
"""

from pathlib import Path
from typing import Any, Dict, Optional

from .utils import read_yaml


class SpecLoader:
    """
    Loads and merges workshop specifications from a spec directory.

    Handles discovery of spec files (workshop.yml, modules.yml, profile.yml,
    project.md, ai_guidelines.md) and provides unified access to all specs.
    """

    def __init__(self, spec_dir: Path):
        """
        Initialize spec loader.

        Args:
            spec_dir: Path to directory containing spec files

        Raises:
            FileNotFoundError: If spec_dir doesn't exist
        """
        if not spec_dir.exists():
            raise FileNotFoundError(f"Spec directory not found: {spec_dir}")

        self.spec_dir = spec_dir.resolve()
        self._specs: Optional[Dict[str, Any]] = None

    def load(self) -> Dict[str, Any]:
        """
        Load all specifications from the spec directory.

        Returns:
            Dictionary with keys: workshop, modules, profile, project, ai_guidelines

        Raises:
            FileNotFoundError: If required spec files are missing
            yaml.YAMLError: If YAML parsing fails
        """
        if self._specs is not None:
            return self._specs

        specs = {
            "workshop": self._load_workshop(),
            "modules": self._load_modules(),
            "profile": self._load_profile(),
            "project": self._load_project(),
            "ai_guidelines": self._load_ai_guidelines(),
        }

        # Add computed metadata
        specs["_meta"] = {
            "spec_dir": str(self.spec_dir),
            "loaded_files": self._list_loaded_files(),
        }

        self._specs = specs
        return specs

    def _load_workshop(self) -> Dict[str, Any]:
        """Load workshop.yml specification."""
        workshop_file = self.spec_dir / "workshop.yml"
        if not workshop_file.exists():
            raise FileNotFoundError(f"Required spec file missing: {workshop_file}")
        return read_yaml(workshop_file)

    def _load_modules(self) -> Dict[str, Any]:
        """Load modules.yml specification."""
        modules_file = self.spec_dir / "modules.yml"
        if not modules_file.exists():
            raise FileNotFoundError(f"Required spec file missing: {modules_file}")
        return read_yaml(modules_file)

    def _load_profile(self) -> Dict[str, Any]:
        """Load profile.yml specification."""
        profile_file = self.spec_dir / "profile.yml"
        if not profile_file.exists():
            # Profile is optional, return defaults
            return {"domain": "general"}
        return read_yaml(profile_file)

    def _load_project(self) -> str:
        """Load project.md content."""
        project_file = self.spec_dir / "project.md"
        if not project_file.exists():
            return ""
        return project_file.read_text(encoding="utf-8")

    def _load_ai_guidelines(self) -> str:
        """Load ai_guidelines.md content."""
        guidelines_file = self.spec_dir / "ai_guidelines.md"
        if not guidelines_file.exists():
            return ""
        return guidelines_file.read_text(encoding="utf-8")

    def _list_loaded_files(self) -> list[str]:
        """Get list of actually loaded spec files."""
        files = []
        for name in ["workshop.yml", "modules.yml", "profile.yml", "project.md", "ai_guidelines.md"]:
            path = self.spec_dir / name
            if path.exists():
                files.append(name)
        return sorted(files)

    def get_workshop(self) -> Dict[str, Any]:
        """Get workshop specification."""
        return self.load()["workshop"]

    def get_modules(self) -> list[Dict[str, Any]]:
        """Get list of module specifications."""
        return self.load()["modules"].get("modules", [])

    def get_profile(self) -> Dict[str, Any]:
        """Get profile specification."""
        return self.load()["profile"]

    def get_project(self) -> str:
        """Get project description."""
        return self.load()["project"]

    def get_ai_guidelines(self) -> str:
        """Get AI generation guidelines."""
        return self.load()["ai_guidelines"]

    def get_module_by_id(self, module_id: str) -> Optional[Dict[str, Any]]:
        """
        Find module by ID.

        Args:
            module_id: Module identifier

        Returns:
            Module spec dict, or None if not found
        """
        for module in self.get_modules():
            if module.get("id") == module_id:
                return module
        return None

    def get_deliverables(self) -> list[str]:
        """
        Get all deliverable paths from all modules.

        Returns:
            Sorted list of deliverable paths
        """
        deliverables = []
        for module in self.get_modules():
            deliverables.extend(module.get("deliverables", []))
        return sorted(set(deliverables))
