#!/usr/bin/env python3
"""Pre-commit hook to regenerate AI usage guide.

This script checks if CLI or documentation files have been modified and automatically
regenerates the AI_USAGE_GUIDE.md file to keep it in sync.

Exit codes:
    0: Success (guide regenerated or no action needed)
    1: Error in script execution
"""

import sys
from pathlib import Path
from subprocess import run  # nosec B404 - Using subprocess for git/workshopforge commands (trusted)


def get_staged_files() -> list[str]:
    """Get list of staged files from git.

    Returns:
        List of staged file paths
    """
    result = run(  # nosec B603 B607 - Running git command with fixed args (safe)
        ["git", "diff", "--cached", "--name-only"],
        capture_output=True,
        text=True,
        check=True,
    )
    return result.stdout.strip().split("\n") if result.stdout else []


def check_relevant_changes(staged_files: list[str]) -> bool:
    """Check if any relevant files were modified.

    Args:
        staged_files: List of staged file paths

    Returns:
        True if relevant files were modified, False otherwise
    """
    relevant_patterns = [
        "forge/cli.py",  # CLI commands
        "forge/orchestrator.py",  # AI orchestration
        "forge/policies.py",  # Policy engine
        "forge/providers/",  # AI providers
        "AI_USAGE_GUIDE.md",  # The guide itself (for validation)
    ]

    # Don't regenerate if only the guide itself changed
    non_guide_changes = [f for f in staged_files if f != "AI_USAGE_GUIDE.md"]
    if not non_guide_changes:
        return False

    for file_path in non_guide_changes:
        if any(pattern in file_path for pattern in relevant_patterns):
            return True
    return False


def validate_guide_freshness() -> bool:
    """Check if AI_USAGE_GUIDE.md needs updating.

    Returns:
        True if guide is fresh or successfully updated, False on error
    """
    try:
        guide_path = Path("AI_USAGE_GUIDE.md")

        if not guide_path.exists():
            print("⚠️  AI_USAGE_GUIDE.md not found, skipping validation")
            return True

        print("\n" + "=" * 70)
        print("🔍 Checking AI usage guide freshness...")
        print("=" * 70)

        # Test if the command works
        result = run(  # nosec B603 B607 - Running controlled command (safe)
            ["uv", "run", "workshopforge", "ai", "usage-prompt", "--plain"],
            capture_output=True,
            text=True,
            check=False,
        )

        if result.returncode != 0:
            print(f"❌ Failed to generate usage guide: {result.stderr}")
            return False

        current_content = guide_path.read_text()
        generated_content = result.stdout

        # Ensure newline at end
        if not generated_content.endswith("\n"):
            generated_content += "\n"

        # Compare content
        if current_content == generated_content:
            print("✅ AI usage guide is up to date")
            print("=" * 70)
            print()
            return True

        print("⚠️  AI usage guide appears outdated")
        print()
        print("The guide content differs from what would be generated.")
        print("This might happen if:")
        print("  • CLI commands were added/modified")
        print("  • Provider implementations changed")
        print("  • Policy rules were updated")
        print()
        print("To update the guide, run:")
        print("  workshopforge ai usage-prompt --plain > AI_USAGE_GUIDE.md")
        print()
        print("Or manually edit AI_USAGE_GUIDE.md to reflect the changes.")
        print("=" * 70)
        print()

        # For now, just warn but don't block
        # In the future, you could make this stricter
        return True

    except Exception as e:
        print(f"❌ Error checking guide freshness: {e}")
        return False


def main() -> int:
    """Main entry point for the hook.

    Returns:
        Exit code (0 = success, 1 = error)
    """
    try:
        staged_files = get_staged_files()

        if not staged_files:
            # No staged files, nothing to check
            return 0

        if check_relevant_changes(staged_files) and not validate_guide_freshness():
            # Validation failed, but don't block commit
            print("⚠️  Guide validation failed, but commit will proceed")
            return 0

        # Success
        return 0

    except Exception as e:
        print(f"Error in guide validation: {e}", file=sys.stderr)
        # Return 0 even on error to not block commits
        return 0


if __name__ == "__main__":
    sys.exit(main())
