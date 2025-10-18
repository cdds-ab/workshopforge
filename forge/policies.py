"""
Policy engine for spec compliance checking.

Enforces workshop quality standards through configurable rules
that validate structure, completeness, and adherence to specifications.
"""

from pathlib import Path
from typing import Any, Dict, List, Optional

from .content_validator import validate_slides
from .loader import SpecLoader


class PolicyViolation:
    """Represents a single policy violation."""

    def __init__(
        self,
        rule_id: str,
        severity: str,
        message: str,
        path: Optional[str] = None,
    ):
        """
        Initialize violation.

        Args:
            rule_id: Unique rule identifier
            severity: "error" or "warn"
            message: Human-readable description
            path: Affected file/resource path (optional)
        """
        self.rule_id = rule_id
        self.severity = severity
        self.message = message
        self.path = path

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for reporting."""
        result = {
            "rule_id": self.rule_id,
            "severity": self.severity,
            "message": self.message,
        }
        if self.path:
            result["path"] = self.path
        return result


class PolicyRule:
    """Base class for policy rules."""

    def __init__(self, rule_id: str, severity: str = "error"):
        """
        Initialize rule.

        Args:
            rule_id: Unique rule identifier
            severity: Default severity ("error" or "warn")
        """
        self.rule_id = rule_id
        self.severity = severity

    def check(self, context: Dict[str, Any]) -> List[PolicyViolation]:
        """
        Check rule against context.

        Args:
            context: Checking context with keys:
                - spec_loader: SpecLoader instance
                - target_dir: Path to generated workshop (if applicable)
                - config: Policy configuration overrides

        Returns:
            List of violations (empty if compliant)
        """
        raise NotImplementedError("Subclasses must implement check()")


class ModuleCompletenessRule(PolicyRule):
    """Verify all modules have required fields."""

    def __init__(self):
        super().__init__("module-completeness", severity="error")

    def check(self, context: Dict[str, Any]) -> List[PolicyViolation]:
        violations = []
        loader: SpecLoader = context["spec_loader"]

        for module in loader.get_modules():
            module_id = module.get("id", "unknown")

            # Check required fields
            if not module.get("objective"):
                violations.append(
                    PolicyViolation(
                        self.rule_id,
                        self.severity,
                        f"Module '{module_id}' missing objective",
                        f"modules.yml#{module_id}",
                    )
                )

            deliverables = module.get("deliverables", [])
            if not deliverables:
                violations.append(
                    PolicyViolation(
                        self.rule_id,
                        self.severity,
                        f"Module '{module_id}' has no deliverables",
                        f"modules.yml#{module_id}",
                    )
                )

            duration = module.get("duration_minutes", 0)
            if duration <= 0:
                violations.append(
                    PolicyViolation(
                        self.rule_id,
                        self.severity,
                        f"Module '{module_id}' has invalid duration: {duration}",
                        f"modules.yml#{module_id}",
                    )
                )

        return violations


class DeliverableExistenceRule(PolicyRule):
    """Verify all declared deliverables exist in generated workshop."""

    def __init__(self):
        super().__init__("deliverable-existence", severity="error")

    def check(self, context: Dict[str, Any]) -> List[PolicyViolation]:
        violations = []
        loader: SpecLoader = context["spec_loader"]
        target_dir: Optional[Path] = context.get("target_dir")

        if not target_dir or not target_dir.exists():
            # Can't check if target doesn't exist yet
            return violations

        for module in loader.get_modules():
            for deliverable in module.get("deliverables", []):
                deliverable_path = target_dir / deliverable

                if not deliverable_path.exists():
                    violations.append(
                        PolicyViolation(
                            self.rule_id,
                            self.severity,
                            f"Deliverable not found: {deliverable}",
                            deliverable,
                        )
                    )

        return violations


class ReadmeRequirementsRule(PolicyRule):
    """Verify README mentions key workshop concepts."""

    def __init__(self):
        super().__init__("readme-requirements", severity="warn")

    def check(self, context: Dict[str, Any]) -> List[PolicyViolation]:
        violations = []
        target_dir: Optional[Path] = context.get("target_dir")

        if not target_dir or not target_dir.exists():
            return violations

        readme_path = target_dir / "README.md"
        if not readme_path.exists():
            violations.append(
                PolicyViolation(
                    self.rule_id,
                    "error",
                    "README.md not found in workshop root",
                    "README.md",
                )
            )
            return violations

        readme_content = readme_path.read_text(encoding="utf-8").lower()

        # Check for key mentions
        required_terms = [
            ("spec", "specifications or spec-driven"),
            ("workshopforge", "workshopforge tool"),
        ]

        for term, description in required_terms:
            if term not in readme_content:
                violations.append(
                    PolicyViolation(
                        self.rule_id,
                        self.severity,
                        f"README should mention {description}",
                        "README.md",
                    )
                )

        return violations


class InstructorSeparationRule(PolicyRule):
    """Verify instructor materials are separated from student content."""

    def __init__(self):
        super().__init__("instructor-separation", severity="error")

    def check(self, context: Dict[str, Any]) -> List[PolicyViolation]:
        violations = []
        target_dir: Optional[Path] = context.get("target_dir")

        if not target_dir or not target_dir.exists():
            return violations

        # Check that instructor/ and reference/ directories exist
        instructor_dir = target_dir / "instructor"
        reference_dir = target_dir / "reference"

        if not instructor_dir.exists():
            violations.append(
                PolicyViolation(
                    self.rule_id,
                    self.severity,
                    "instructor/ directory not found",
                    "instructor/",
                )
            )

        if not reference_dir.exists():
            violations.append(
                PolicyViolation(
                    self.rule_id,
                    self.severity,
                    "reference/ directory not found",
                    "reference/",
                )
            )

        return violations


class ForbiddenPatternsRule(PolicyRule):
    """Check for forbidden patterns in generated content."""

    def __init__(self):
        super().__init__("forbidden-patterns", severity="warn")

    def check(self, context: Dict[str, Any]) -> List[PolicyViolation]:
        violations = []
        target_dir: Optional[Path] = context.get("target_dir")

        if not target_dir or not target_dir.exists():
            return violations

        # Forbidden patterns in student-facing content
        forbidden = ["TODO", "FIXME", "XXX"]

        # Check labs directory for forbidden patterns
        labs_dir = target_dir / "labs"
        if labs_dir.exists():
            for md_file in labs_dir.rglob("*.md"):
                content = md_file.read_text(encoding="utf-8")
                for pattern in forbidden:
                    if pattern in content:
                        violations.append(
                            PolicyViolation(
                                self.rule_id,
                                self.severity,
                                f"Found '{pattern}' in student materials",
                                str(md_file.relative_to(target_dir)),
                            )
                        )
                        break  # One violation per file is enough

        return violations


class NamingConventionRule(PolicyRule):
    """Verify module IDs follow naming conventions."""

    def __init__(self):
        super().__init__("naming-convention", severity="warn")

    def check(self, context: Dict[str, Any]) -> List[PolicyViolation]:
        import re

        violations = []
        loader: SpecLoader = context["spec_loader"]

        # Module IDs should be lowercase-with-dashes
        pattern = re.compile(r"^[a-z0-9-]+$")

        for module in loader.get_modules():
            module_id = module.get("id", "")
            if not pattern.match(module_id):
                violations.append(
                    PolicyViolation(
                        self.rule_id,
                        self.severity,
                        f"Module ID '{module_id}' doesn't follow convention (lowercase-with-dashes)",
                        f"modules.yml#{module_id}",
                    )
                )

        return violations


class SlideContentRule(PolicyRule):
    """
    Verify slide content follows evidence-based cognitive science principles.

    Based on:
    - Working Memory Capacity: 3-5 items (Cowan, 2010)
    - Cognitive Load Theory (Sweller et al., 2019)
    - Chunking principle for code examples
    - Mayer's Multimedia Learning principles
    """

    def __init__(self):
        super().__init__("slide-content-quality", severity="error")

    def check(self, context: Dict[str, Any]) -> List[PolicyViolation]:
        violations = []
        target_dir: Optional[Path] = context.get("target_dir")

        if not target_dir or not target_dir.exists():
            return violations

        # Check instructor slides directory
        slides_dir = target_dir / "instructor" / "slides"
        if not slides_dir.exists():
            return violations

        # Use SlideValidator to check all slides
        content_violations = validate_slides(slides_dir)

        # Convert ContentViolation to PolicyViolation
        for slide_file, content_violations_list in content_violations.items():
            for cv in content_violations_list:
                rel_path = slide_file.relative_to(target_dir)
                violations.append(
                    PolicyViolation(
                        self.rule_id,
                        self.severity,
                        f"{cv.message}",
                        f"{rel_path}:{cv.line}",
                    )
                )

        return violations


class PolicyEngine:
    """
    Orchestrates policy rule checking.

    Loads rules, applies them to workshop context, and collects violations.
    """

    DEFAULT_RULES = [
        ModuleCompletenessRule,
        DeliverableExistenceRule,
        ReadmeRequirementsRule,
        InstructorSeparationRule,
        ForbiddenPatternsRule,
        NamingConventionRule,
        SlideContentRule,
    ]

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize policy engine.

        Args:
            config: Optional configuration overrides
        """
        self.config = config or {}
        self.rules: List[PolicyRule] = []

        # Load default rules
        for rule_class in self.DEFAULT_RULES:
            self.rules.append(rule_class())

    def check(
        self,
        spec_loader: SpecLoader,
        target_dir: Optional[Path] = None,
    ) -> List[PolicyViolation]:
        """
        Run all policy checks.

        Args:
            spec_loader: Loaded specifications
            target_dir: Generated workshop directory (optional)

        Returns:
            List of all violations across all rules
        """
        context = {
            "spec_loader": spec_loader,
            "target_dir": target_dir,
            "config": self.config,
        }

        violations = []
        for rule in self.rules:
            violations.extend(rule.check(context))

        return violations

    def has_errors(self, violations: List[PolicyViolation]) -> bool:
        """Check if violations contain any errors (vs just warnings)."""
        return any(v.severity == "error" for v in violations)

    def filter_allowed(
        self,
        violations: List[PolicyViolation],
        allowed_rules: List[str],
    ) -> List[PolicyViolation]:
        """
        Filter violations, removing allowed rule IDs.

        Args:
            violations: All violations
            allowed_rules: List of rule IDs to ignore

        Returns:
            Filtered violation list
        """
        return [v for v in violations if v.rule_id not in allowed_rules]
