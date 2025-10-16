"""
Stable prompt prelude generation for AI operations.

Creates a consistent, hashable summary of workshop specifications
that is prepended to every AI request to maintain session-spanning
context stability.
"""

from pathlib import Path
from typing import Dict, Any

from .loader import SpecLoader
from .utils import compute_hash


class PreludeGenerator:
    """
    Generates stable, spec-derived prelude text for AI prompts.

    The prelude distills workshop specs into a concise context summary
    that prevents LLM drift across sessions by always providing the
    same foundational knowledge.
    """

    def __init__(self, spec_loader: SpecLoader):
        """
        Initialize prelude generator.

        Args:
            spec_loader: Loaded specification data
        """
        self.loader = spec_loader
        self._prelude_text: str = ""
        self._prelude_hash: str = ""

    def generate(self) -> str:
        """
        Generate stable prelude text from specifications.

        Returns:
            Formatted prelude text for AI context
        """
        specs = self.loader.load()
        workshop = specs["workshop"]
        modules = self.loader.get_modules()
        profile = specs["profile"]
        project = specs["project"]
        ai_guidelines = specs["ai_guidelines"]

        # Build prelude sections
        sections = [
            "# Workshop Specification Context",
            "",
            f"**Workshop ID:** {workshop['id']}",
            f"**Title:** {workshop['title']}",
            f"**Version:** {workshop['version']}",
            f"**Audience:** {workshop['audience']}",
            f"**Domain:** {profile['domain']}",
            "",
            "## Structure and Policies",
            "",
            f"- Duration: {workshop['duration']['groups']} groups × "
            f"{workshop['duration']['sessions_per_group']} sessions "
            f"({workshop['duration']['session_minutes']} min each)",
            f"- Student AI usage: **{workshop['policy']['student_ai_usage']}**",
            f"- License: {workshop['policy']['license']}",
            f"- Outputs: slides={workshop.get('outputs', {}).get('slides', True)}, "
            f"handouts={workshop.get('outputs', {}).get('handouts', True)}",
            "",
            "## Repository Structure",
            "",
            "```",
            f"{workshop['id']}/",
            "  spec/          # Specifications (source of truth)",
            "  labs/          # Student exercises",
            "  instructor/    # Instructor-only materials",
            "  reference/     # Reference solutions",
            "```",
            "",
            "## Learning Modules",
            "",
        ]

        # Add modules with objectives and deliverables
        for i, module in enumerate(modules, 1):
            sections.extend([
                f"### {i}. {module.get('title', module['id'])} (`{module['id']}`)",
                f"**Objective:** {module['objective']}",
                f"**Duration:** {module['duration_minutes']} min",
                "**Deliverables:**",
            ])
            for deliverable in module.get("deliverables", []):
                sections.append(f"  - `{deliverable}`")
            if module.get("depends_on"):
                sections.append(f"**Prerequisites:** {', '.join(module['depends_on'])}")
            sections.append("")

        # Add project context if available
        if project:
            sections.extend([
                "## Project Context",
                "",
                project.strip(),
                "",
            ])

        # Add AI generation guidelines if available
        if ai_guidelines:
            sections.extend([
                "## AI Generation Guidelines",
                "",
                ai_guidelines.strip(),
                "",
            ])

        # Add standard constraints
        sections.extend([
            "## Constraints and Rules",
            "",
            "1. All generated content MUST align with module objectives",
            "2. All declared deliverables MUST be created",
            "3. Student AI policy MUST be respected in materials",
            "4. File naming follows spec conventions (lowercase, dashes)",
            "5. Instructor vs student separation MUST be maintained",
            "6. Code and documentation are written in English",
            "7. Generated materials reference their spec source (e.g., `modules.yml#module-id`)",
            "",
            "---",
            "",
            "Use this context to ensure all AI-generated content is spec-compliant,",
            "consistent across sessions, and aligned with workshop objectives.",
        ])

        self._prelude_text = "\n".join(sections)
        self._prelude_hash = compute_hash(self._prelude_text)

        return self._prelude_text

    def get_hash(self) -> str:
        """
        Get hash of current prelude (generate if needed).

        Returns:
            16-character hex hash of prelude text
        """
        if not self._prelude_hash:
            self.generate()
        return self._prelude_hash

    def save(self, output_path: Path) -> None:
        """
        Save prelude text to file.

        Args:
            output_path: Where to write prelude
        """
        if not self._prelude_text:
            self.generate()

        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(self._prelude_text, encoding="utf-8")

    def build_messages(self, user_goal: str) -> list[Dict[str, str]]:
        """
        Build message list for AI provider with prelude + user goal.

        Args:
            user_goal: User's request or goal

        Returns:
            List of message dicts for AI provider
        """
        if not self._prelude_text:
            self.generate()

        return [
            {
                "role": "system",
                "content": self._prelude_text,
            },
            {
                "role": "user",
                "content": user_goal,
            },
        ]
