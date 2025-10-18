"""
Content quality validator for generated workshop materials.

Validates slides, labs, and other generated content against quality rules
defined in spec/ai_guidelines.md.
"""

import re
from pathlib import Path
from typing import Dict, List


class ContentViolation:
    """Represents a content quality violation."""

    def __init__(self, file: Path, line: int, rule: str, message: str):
        self.file = file
        self.line = line
        self.rule = rule
        self.message = message

    def __str__(self) -> str:
        return f"{self.file}:{self.line} [{self.rule}] {self.message}"


class SlideValidator:
    """
    Validates Marp slides against evidence-based quality rules.

    Based on cognitive science research:
    - Working memory: 3-5 items (Cowan, 2010)
    - Cognitive Load Theory (Sweller et al., 2019)
    - Chunking principle for code examples
    - Mayer's Multimedia Learning principles
    """

    MAX_CODE_LINES = 12  # Chunking principle: manageable pieces
    MAX_BULLETS = 5  # Working memory limit (7±2 rule, refined to 3-5)
    MAX_TOTAL_LINES = 15  # Coherence principle: less is better

    def __init__(self):
        self.violations: List[ContentViolation] = []

    def validate_file(self, slide_file: Path) -> List[ContentViolation]:
        """
        Validate a single slide file.

        Args:
            slide_file: Path to Markdown slide file

        Returns:
            List of violations found
        """
        self.violations = []

        if not slide_file.exists():
            return self.violations

        with open(slide_file, "r", encoding="utf-8") as f:
            lines = f.readlines()

        self._check_code_blocks(lines, slide_file)
        self._check_bullet_lists(lines, slide_file)
        self._check_slide_titles(lines, slide_file)
        self._check_total_content_per_slide(lines, slide_file)

        return self.violations

    def _check_code_blocks(self, lines: List[str], file: Path):
        """Check code block lengths."""
        in_code = False
        code_start = 0
        code_lines = 0

        for i, line in enumerate(lines, 1):
            if line.strip().startswith("```"):
                if not in_code:
                    # Start of code block
                    in_code = True
                    code_start = i
                    code_lines = 0
                else:
                    # End of code block
                    in_code = False
                    if code_lines > self.MAX_CODE_LINES:
                        self.violations.append(
                            ContentViolation(
                                file=file,
                                line=code_start,
                                rule="code-block-length",
                                message=f"Code block has {code_lines} lines (max {self.MAX_CODE_LINES}). "
                                f"Split into multiple slides with (1/2), (2/2) notation.",
                            )
                        )
            elif in_code:
                code_lines += 1

    def _check_bullet_lists(self, lines: List[str], file: Path):
        """Check bullet list lengths per slide."""
        bullet_count = 0
        slide_start = 0

        for i, line in enumerate(lines, 1):
            stripped = line.strip()

            # New slide
            if stripped == "---":
                if bullet_count > self.MAX_BULLETS:
                    self.violations.append(
                        ContentViolation(
                            file=file,
                            line=slide_start,
                            rule="bullet-count",
                            message=f"Slide has {bullet_count} bullet points (max {self.MAX_BULLETS}). "
                            f"Split content across multiple slides.",
                        )
                    )
                bullet_count = 0
                slide_start = i + 1

            # Bullet point
            elif stripped.startswith(("- ", "* ", "+ ", "✅ ", "❌ ")):
                bullet_count += 1

        # Check last slide
        if bullet_count > self.MAX_BULLETS:
            self.violations.append(
                ContentViolation(
                    file=file,
                    line=slide_start,
                    rule="bullet-count",
                    message=f"Slide has {bullet_count} bullet points (max {self.MAX_BULLETS})",
                )
            )

    def _check_slide_titles(self, lines: List[str], file: Path):
        """Check for proper split slide numbering."""
        for i, line in enumerate(lines, 1):
            # Look for titles with potential split indicators
            if line.startswith("##"):
                # Check for inconsistent split notation
                if "(1/" in line and not re.search(r"\(\d+/\d+\)$", line.strip()):
                    self.violations.append(
                        ContentViolation(
                            file=file,
                            line=i,
                            rule="split-notation",
                            message="Split slide notation should be at end of title: '## Title (1/2)'",
                        )
                    )

    def _check_total_content_per_slide(self, lines: List[str], file: Path):
        """Check total content lines per slide (cognitive load)."""
        slide_start = 0
        content_lines = 0
        in_code = False

        for i, line in enumerate(lines, 1):
            stripped = line.strip()

            # New slide
            if stripped == "---":
                if content_lines > self.MAX_TOTAL_LINES:
                    self.violations.append(
                        ContentViolation(
                            file=file,
                            line=slide_start,
                            rule="total-content",
                            message=f"Slide has {content_lines} content lines (max {self.MAX_TOTAL_LINES}). "
                            f"Split into multiple slides - Cognitive Load Theory suggests less is better.",
                        )
                    )
                content_lines = 0
                slide_start = i + 1
                in_code = False
                continue

            # Track code blocks
            if stripped.startswith("```"):
                in_code = not in_code
                continue

            # Count content lines (skip headers, empty lines)
            if stripped and not stripped.startswith("#"):
                content_lines += 1


def validate_slides(slides_dir: Path) -> Dict[Path, List[ContentViolation]]:
    """
    Validate all slides in a directory.

    Args:
        slides_dir: Directory containing slide Markdown files

    Returns:
        Dictionary mapping slide files to their violations
    """
    validator = SlideValidator()
    results = {}

    if not slides_dir.exists():
        return results

    for slide_file in slides_dir.glob("*.md"):
        violations = validator.validate_file(slide_file)
        if violations:
            results[slide_file] = violations

    return results


def print_violations(violations_by_file: Dict[Path, List[ContentViolation]]):
    """Print violations in a readable format."""
    if not violations_by_file:
        print("✓ No content violations found!")
        return

    total = sum(len(v) for v in violations_by_file.values())
    print(f"❌ Found {total} content violations:\n")

    for file, violations in violations_by_file.items():
        print(f"\n{file}:")
        for violation in violations:
            print(f"  Line {violation.line}: [{violation.rule}] {violation.message}")
