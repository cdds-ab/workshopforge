"""
Template-based workshop repository generator.

Materializes workshop structure from specifications using Jinja2 templates
with deterministic output for reproducibility.
"""

from pathlib import Path
from typing import Any, Dict

from jinja2 import Environment, FileSystemLoader, select_autoescape

from .loader import SpecLoader
from .utils import ensure_dir, timestamp


class WorkshopGenerator:
    """
    Generates workshop repository structure from specs and templates.

    Uses Jinja2 templates to render README, labs, instructor materials,
    and CI configuration deterministically.
    """

    def __init__(self, spec_loader: SpecLoader, template_dir: Path):
        """
        Initialize generator.

        Args:
            spec_loader: Loaded specifications
            template_dir: Path to template directory

        Raises:
            FileNotFoundError: If template_dir doesn't exist
        """
        if not template_dir.exists():
            raise FileNotFoundError(f"Template directory not found: {template_dir}")

        self.loader = spec_loader
        self.template_dir = template_dir.resolve()

        # Set up Jinja2 environment
        self.jinja = Environment(
            loader=FileSystemLoader(self.template_dir),
            autoescape=select_autoescape(["html", "xml"]),
            trim_blocks=True,
            lstrip_blocks=True,
        )

        # Add custom filters
        self.jinja.filters["basename"] = lambda p: Path(p).name
        self.jinja.filters["dirname"] = lambda p: str(Path(p).parent)

    def generate(self, target_dir: Path) -> None:
        """
        Generate complete workshop repository.

        Args:
            target_dir: Output directory for generated workshop

        Raises:
            RuntimeError: If generation fails
        """
        ensure_dir(target_dir)

        specs = self.loader.load()
        workshop = specs["workshop"]
        modules = self.loader.get_modules()
        profile = specs["profile"]

        context = {
            "workshop": workshop,
            "modules": modules,
            "profile": profile,
            "generated_at": timestamp(),
        }

        # Generate root files
        self._render_template("repo/README.md.j2", target_dir / "README.md", context)
        self._render_template("repo/COURSE.md.j2", target_dir / "COURSE.md", context)

        # Generate labs for each module
        self._generate_labs(target_dir, modules, context)

        # Generate instructor materials
        self._generate_instructor_materials(target_dir, context)

        # Generate reference directory
        ensure_dir(target_dir / "reference")
        (target_dir / "reference" / ".keep").touch()

        # Generate CI workflows if enabled
        ci_config = profile.get("ci", {})
        if ci_config.get("enable_basic_checks", True):
            self._generate_ci(target_dir, context)

    def _render_template(
        self, template_path: str, output_path: Path, context: Dict[str, Any]
    ) -> None:
        """
        Render single template to output file.

        Args:
            template_path: Relative path to template in template_dir
            output_path: Output file path
            context: Template context data
        """
        template = self.jinja.get_template(template_path)
        rendered = template.render(**context)

        ensure_dir(output_path.parent)
        output_path.write_text(rendered, encoding="utf-8")

    def _generate_labs(
        self, target_dir: Path, modules: list[Dict[str, Any]], context: Dict[str, Any]
    ) -> None:
        """
        Generate lab directories and READMEs for all modules.

        Args:
            target_dir: Output directory
            modules: List of module specifications
            context: Base template context
        """
        labs_dir = target_dir / "labs"
        ensure_dir(labs_dir)

        # Generate per-module lab READMEs
        for module in sorted(modules, key=lambda m: m["id"]):
            module_dir = labs_dir / module["id"]
            ensure_dir(module_dir)

            module_context = {**context, "module": module}
            readme_path = module_dir / "README.md"
            self._render_template("repo/labs/_module_README.md.j2", readme_path, module_context)

    def _generate_instructor_materials(self, target_dir: Path, context: Dict[str, Any]) -> None:
        """
        Generate instructor slides and notes.

        Args:
            target_dir: Output directory
            context: Template context
        """
        instructor_dir = target_dir / "instructor"
        ensure_dir(instructor_dir / "slides")
        ensure_dir(instructor_dir / "notes")

        # Generate slide deck
        self._render_template(
            "repo/instructor/slides/slide_deck.md.j2",
            instructor_dir / "slides" / "slides.md",
            context,
        )

        # Generate instructor notes
        self._render_template(
            "repo/instructor/notes/notes.md.j2",
            instructor_dir / "notes" / "notes.md",
            context,
        )

    def _generate_ci(self, target_dir: Path, context: Dict[str, Any]) -> None:
        """
        Generate CI workflow configuration.

        Args:
            target_dir: Output directory
            context: Template context
        """
        github_dir = target_dir / ".github" / "workflows"
        ensure_dir(github_dir)

        self._render_template(
            "repo/.github/workflows/basic_checks.yml.j2",
            github_dir / "basic_checks.yml",
            context,
        )


def promote_to_student_pack(instructor_dir: Path, student_dir: Path, redactions: list[str]) -> None:
    """
    Create student pack from instructor materials by applying redactions.

    Args:
        instructor_dir: Source instructor materials
        student_dir: Target student pack directory
        redactions: List of glob patterns to exclude

    Raises:
        FileNotFoundError: If instructor_dir doesn't exist
    """
    import shutil
    from fnmatch import fnmatch

    if not instructor_dir.exists():
        raise FileNotFoundError(f"Instructor directory not found: {instructor_dir}")

    ensure_dir(student_dir)

    # Default redactions if none provided
    if not redactions:
        redactions = ["instructor/**", "reference/**"]

    # Copy all files except redacted patterns
    for item in instructor_dir.rglob("*"):
        if item.is_file():
            rel_path = item.relative_to(instructor_dir)

            # Check if path matches any redaction pattern
            should_exclude = any(fnmatch(str(rel_path), pattern) for pattern in redactions)

            if not should_exclude:
                target_path = student_dir / rel_path
                ensure_dir(target_path.parent)
                shutil.copy2(item, target_path)
