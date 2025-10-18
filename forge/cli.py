"""
Command-line interface for WorkshopForge.

Provides all user-facing commands: init, validate, generate, promote,
and AI operations (plan, apply, check, explain).
"""

from pathlib import Path
from typing import Optional

import typer
from rich import print as rprint
from rich.console import Console
from rich.markdown import Markdown

from . import __version__
from .content_validator import validate_slides
from .generator import WorkshopGenerator, promote_to_student_pack
from .loader import SpecLoader
from .orchestrator import AIOrchestrator
from .utils import ensure_dir, write_yaml
from .validator import SpecValidator

app = typer.Typer(
    name="workshopforge",
    help="Spec-driven workshop generator with AI orchestration",
    add_completion=False,
)
ai_app = typer.Typer(help="AI orchestration commands")
app.add_typer(ai_app, name="ai")

console = Console()


def version_callback(value: bool):
    """Print version and exit."""
    if value:
        rprint(f"workshopforge version {__version__}")
        raise typer.Exit()


@app.callback()
def main(
    version: bool = typer.Option(
        None,
        "--version",
        "-v",
        help="Show version",
        callback=version_callback,
        is_eager=True,
    ),
):
    """WorkshopForge: Spec-first workshop generator with AI orchestration."""
    pass


@app.command()
def init(
    path: Path = typer.Argument(..., help="Directory to initialize"),
    force: bool = typer.Option(False, "--force", "-f", help="Overwrite existing files"),
):
    """
    Initialize a new workshop with minimal spec files.

    Creates spec/ directory with example workshop.yml, modules.yml,
    profile.yml, project.md, and ai_guidelines.md files.
    """
    path = path.resolve()

    if path.exists() and not force:
        if any(path.iterdir()):
            rprint(
                f"[red]Error:[/red] Directory {path} exists and is not empty. Use --force to overwrite."
            )
            raise typer.Exit(1)

    ensure_dir(path)
    spec_dir = ensure_dir(path / "spec")

    rprint(f"[blue]Initializing workshop in:[/blue] {path}")

    # Create example workshop.yml
    workshop_spec = {
        "id": "example-workshop",
        "title": "Example Workshop",
        "version": "1.0.0",
        "audience": "Developers learning WorkshopForge",
        "duration": {
            "groups": 1,
            "sessions_per_group": 3,
            "session_minutes": 60,
        },
        "policy": {
            "student_ai_usage": "allowed",
            "license": "CC-BY-4.0",
        },
        "outputs": {
            "slides": True,
            "handouts": True,
        },
        "branding": {
            "org": "Your Organization",
            "theme": "default",
        },
    }
    write_yaml(spec_dir / "workshop.yml", workshop_spec)
    rprint("  [green]✓[/green] Created spec/workshop.yml")

    # Create example modules.yml
    modules_spec = {
        "modules": [
            {
                "id": "setup",
                "title": "Environment Setup",
                "objective": "Set up development environment and verify installation",
                "deliverables": ["labs/setup/README.md", "labs/setup/verify.sh"],
                "duration_minutes": 30,
            },
            {
                "id": "fundamentals",
                "title": "Core Fundamentals",
                "objective": "Understand core concepts and implement basic examples",
                "deliverables": ["labs/fundamentals/README.md", "labs/fundamentals/example.py"],
                "duration_minutes": 60,
                "depends_on": ["setup"],
            },
            {
                "id": "advanced",
                "title": "Advanced Topics",
                "objective": "Apply advanced patterns and best practices",
                "deliverables": ["labs/advanced/README.md", "labs/advanced/project/"],
                "duration_minutes": 90,
                "depends_on": ["fundamentals"],
            },
        ]
    }
    write_yaml(spec_dir / "modules.yml", modules_spec)
    rprint("  [green]✓[/green] Created spec/modules.yml")

    # Create example profile.yml
    profile_spec = {
        "domain": "software development",
        "materials": {
            "slides_format": "pdf",
            "deck_engine": "revealjs",
        },
        "student_pack": {
            "include_solutions": False,
            "redactions": ["instructor/**", "reference/**"],
        },
        "ci": {
            "enable_basic_checks": True,
        },
    }
    write_yaml(spec_dir / "profile.yml", profile_spec)
    rprint("  [green]✓[/green] Created spec/profile.yml")

    # Create project.md
    project_md = """# Project Context

This workshop teaches participants how to use WorkshopForge to create
spec-driven, AI-managed workshops.

## Storyline

Participants will learn by doing:
1. Understanding the spec-first approach
2. Generating workshop materials deterministically
3. Using AI orchestration with policy enforcement
4. Maintaining consistency across sessions

## Pedagogical Notes

- Hands-on exercises reinforce concepts
- Progression from simple to complex
- Real-world scenarios and examples
"""
    (spec_dir / "project.md").write_text(project_md, encoding="utf-8")
    rprint("  [green]✓[/green] Created spec/project.md")

    # Create ai_guidelines.md
    ai_guidelines = """# AI Generation Guidelines

## Style
- Clear, concise instructions
- Code examples with explanations
- British English spelling for docs

## Structure
- Progressive difficulty
- Self-contained modules
- Consistent formatting

## Constraints
- No placeholder/TODO content in student materials
- All code must be tested and working
- Reference spec sources in generated files
"""
    (spec_dir / "ai_guidelines.md").write_text(ai_guidelines, encoding="utf-8")
    rprint("  [green]✓[/green] Created spec/ai_guidelines.md")

    # Create README
    readme = f"""# {workshop_spec['title']}

Workshop initialized with WorkshopForge.

## Next Steps

1. Edit specs in `spec/` directory
2. Validate: `workshopforge validate`
3. Generate: `workshopforge generate --target out/instructor`
4. Check compliance: `workshopforge ai check`

## Structure

```
{path.name}/
  spec/          # Workshop specifications (edit these)
  out/           # Generated content (do not edit directly)
```
"""
    (path / "README.md").write_text(readme, encoding="utf-8")
    rprint("  [green]✓[/green] Created README.md")

    rprint("\n[green]✓ Workshop initialized![/green]")
    rprint(f"\nNext: cd {path.name} && workshopforge validate")


@app.command()
def validate(
    spec_dir: Path = typer.Option(
        Path("spec"),
        "--spec-dir",
        help="Path to spec directory",
    ),
):
    """
    Validate workshop specifications against JSON schemas.

    Checks workshop.yml, modules.yml, and profile.yml for correctness.
    """
    spec_dir = spec_dir.resolve()

    if not spec_dir.exists():
        rprint(f"[red]Error:[/red] Spec directory not found: {spec_dir}")
        raise typer.Exit(1)

    rprint(f"[blue]Validating specs in:[/blue] {spec_dir}")

    # Get schema directory (in package)
    schema_dir = Path(__file__).parent / "schemas"
    validator = SpecValidator(schema_dir)

    results = validator.validate_directory(spec_dir)

    if not results:
        rprint("[green]✓ All specs valid![/green]")
        return

    # Print errors
    rprint("[red]✗ Validation errors found:[/red]\n")
    for spec_name, errors in results.items():
        rprint(f"[yellow]{spec_name}.yml:[/yellow]")
        for error in errors:
            rprint(f"  • {error}")
        rprint()

    raise typer.Exit(1)


@app.command()
def generate(
    spec_dir: Path = typer.Option(
        Path("spec"),
        "--spec-dir",
        help="Path to spec directory",
    ),
    target: Path = typer.Option(
        Path("out/instructor"),
        "--target",
        "-t",
        help="Output directory for generated workshop",
    ),
):
    """
    Generate workshop repository from specifications.

    Creates complete workshop structure with labs, instructor materials,
    and CI configuration.
    """
    spec_dir = spec_dir.resolve()
    target = target.resolve()

    if not spec_dir.exists():
        rprint(f"[red]Error:[/red] Spec directory not found: {spec_dir}")
        raise typer.Exit(1)

    rprint(f"[blue]Generating workshop from:[/blue] {spec_dir}")
    rprint(f"[blue]Output to:[/blue] {target}")

    # Load specs
    try:
        loader = SpecLoader(spec_dir)
        loader.load()
    except Exception as e:
        rprint(f"[red]Error loading specs:[/red] {e}")
        raise typer.Exit(1)

    # Generate
    template_dir = Path(__file__).parent / "templates"
    generator = WorkshopGenerator(loader, template_dir)

    try:
        generator.generate(target)
        rprint("\n[green]✓ Workshop generated successfully![/green]")
        rprint(f"\nOutput: {target}")
    except Exception as e:
        rprint(f"[red]Error generating workshop:[/red] {e}")
        raise typer.Exit(1)


@app.command()
def promote(
    instructor_dir: Path = typer.Argument(..., help="Instructor materials directory"),
    student_dir: Path = typer.Argument(..., help="Student pack output directory"),
    redactions: Optional[str] = typer.Option(
        None,
        "--redactions",
        "-r",
        help="Comma-separated glob patterns to exclude (default: instructor/**,reference/**)",
    ),
):
    """
    Create student pack from instructor materials.

    Copies materials while excluding instructor-only content
    based on redaction patterns.
    """
    instructor_dir = instructor_dir.resolve()
    student_dir = student_dir.resolve()

    if not instructor_dir.exists():
        rprint(f"[red]Error:[/red] Instructor directory not found: {instructor_dir}")
        raise typer.Exit(1)

    rprint("[blue]Promoting to student pack...[/blue]")
    rprint(f"  Source: {instructor_dir}")
    rprint(f"  Target: {student_dir}")

    # Parse redactions
    redaction_list = []
    if redactions:
        redaction_list = [r.strip() for r in redactions.split(",")]
    else:
        redaction_list = ["instructor/**", "reference/**"]

    rprint(f"  Redactions: {', '.join(redaction_list)}")

    try:
        promote_to_student_pack(instructor_dir, student_dir, redaction_list)
        rprint("\n[green]✓ Student pack created![/green]")
        rprint(f"\nOutput: {student_dir}")
    except Exception as e:
        rprint(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)


@app.command()
def validate_content(
    slides_dir: Path = typer.Argument(
        ..., help="Directory containing slide Markdown files to validate"
    ),
):
    """
    Validate slide content against cognitive science principles.

    Checks slides for evidence-based quality violations:
    - Max 12 lines per code block (chunking principle)
    - Max 5 bullet points (working memory limit, Cowan 2010)
    - Max 15 total content lines (coherence principle, CLT)
    - Split notation format (1/2, 2/2)

    Based on:
    - Working Memory Capacity: 3-5 items (Cowan, 2010)
    - Cognitive Load Theory (Sweller et al., 2019)
    - Mayer's Multimedia Learning principles
    """
    slides_dir = slides_dir.resolve()

    if not slides_dir.exists():
        rprint(f"[red]Error:[/red] Slides directory not found: {slides_dir}")
        raise typer.Exit(1)

    if not slides_dir.is_dir():
        rprint(f"[red]Error:[/red] Path is not a directory: {slides_dir}")
        raise typer.Exit(1)

    rprint(f"[blue]Validating slides in:[/blue] {slides_dir}\n")

    try:
        violations = validate_slides(slides_dir)

        if not violations:
            rprint("[green]✓ All slides pass cognitive science validation![/green]")
            rprint("No content violations found.")
            return

        # Count total violations
        total = sum(len(v) for v in violations.values())
        rprint(f"[red]✗ Found {total} content violation(s)[/red]\n")

        # Print violations by file
        for slide_file, violations_list in violations.items():
            rel_path = slide_file.relative_to(slides_dir)
            rprint(f"[yellow]{rel_path}:[/yellow]")
            for v in violations_list:
                rprint(f"  Line {v.line}: [{v.rule}] {v.message}")
            rprint()

        raise typer.Exit(1)

    except Exception as e:
        rprint(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)


@ai_app.command("plan")
def ai_plan(
    goal: str = typer.Argument(..., help="User goal for AI generation"),
    spec_dir: Path = typer.Option(
        Path("spec"),
        "--spec-dir",
        help="Path to spec directory",
    ),
    provider: str = typer.Option(
        "echo",
        "--provider",
        "-p",
        help="AI provider (echo, openai, anthropic)",
    ),
):
    """
    Generate AI plan from user goal (no writes).

    Produces a detailed plan with rationale, steps, and policy risks
    without making any changes.
    """
    spec_dir = spec_dir.resolve()

    if not spec_dir.exists():
        rprint(f"[red]Error:[/red] Spec directory not found: {spec_dir}")
        raise typer.Exit(1)

    rprint(f"[blue]Generating plan with {provider} provider...[/blue]")
    rprint(f"Goal: {goal}\n")

    try:
        loader = SpecLoader(spec_dir)
        orchestrator = AIOrchestrator(loader, provider)

        plan = orchestrator.plan(goal)

        # Display plan
        rprint("[green]Plan generated![/green]\n")
        rprint(plan["response_text"])
        rprint(f"\n[dim]Spec hash: {plan['spec_hash']}[/dim]")
        rprint("[dim]Logged to: ai_logs/[/dim]")

    except Exception as e:
        rprint(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)


@ai_app.command("apply")
def ai_apply(
    goal: str = typer.Argument(..., help="User goal for AI generation"),
    spec_dir: Path = typer.Option(
        Path("spec"),
        "--spec-dir",
        help="Path to spec directory",
    ),
    provider: str = typer.Option(
        "echo",
        "--provider",
        "-p",
        help="AI provider (echo, openai, anthropic)",
    ),
    allow_violations: Optional[str] = typer.Option(
        None,
        "--allow-violations",
        help="Comma-separated rule IDs to ignore",
    ),
):
    """
    Execute AI plan with policy enforcement.

    Generates content, runs policy checks, and writes changes
    if compliant (or violations are explicitly allowed).
    """
    spec_dir = spec_dir.resolve()

    if not spec_dir.exists():
        rprint(f"[red]Error:[/red] Spec directory not found: {spec_dir}")
        raise typer.Exit(1)

    rprint(f"[blue]Applying changes with {provider} provider...[/blue]")
    rprint(f"Goal: {goal}\n")

    # Parse allowed violations
    allowed = []
    if allow_violations:
        allowed = [v.strip() for v in allow_violations.split(",")]

    try:
        loader = SpecLoader(spec_dir)
        orchestrator = AIOrchestrator(loader, provider)

        result = orchestrator.apply(goal, allowed)

        if result["success"]:
            rprint(f"[green]✓ {result['message']}[/green]")
            rprint(f"\nChanges applied: {len(result['changes'])}")
        else:
            rprint(f"[red]✗ {result['message']}[/red]")
            rprint("\nSee reports/compliance.md for details")

        rprint("\n[dim]Compliance report: reports/compliance.md[/dim]")

    except Exception as e:
        rprint(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)


@ai_app.command("check")
def ai_check(
    spec_dir: Path = typer.Option(
        Path("spec"),
        "--spec-dir",
        help="Path to spec directory",
    ),
    target_dir: Optional[Path] = typer.Option(
        None,
        "--target-dir",
        help="Generated workshop directory to check",
    ),
):
    """
    Run compliance checks on workshop.

    Validates spec adherence, completeness, and quality standards
    without making changes.
    """
    spec_dir = spec_dir.resolve()

    if not spec_dir.exists():
        rprint(f"[red]Error:[/red] Spec directory not found: {spec_dir}")
        raise typer.Exit(1)

    if target_dir:
        target_dir = target_dir.resolve()
        if not target_dir.exists():
            rprint(f"[red]Error:[/red] Target directory not found: {target_dir}")
            raise typer.Exit(1)

    rprint("[blue]Running compliance checks...[/blue]\n")

    try:
        loader = SpecLoader(spec_dir)
        orchestrator = AIOrchestrator(loader)

        violations = orchestrator.check(target_dir)

        if not violations:
            rprint("[green]✓ All checks passed![/green] No violations found.")
        else:
            errors = [v for v in violations if v.severity == "error"]
            warnings = [v for v in violations if v.severity == "warn"]

            rprint("[yellow]Violations found:[/yellow]")
            rprint(f"  Errors: {len(errors)}")
            rprint(f"  Warnings: {len(warnings)}")
            rprint("\nSee reports/compliance.md for details")

    except Exception as e:
        rprint(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)


@ai_app.command("explain")
def ai_explain(
    path: str = typer.Argument(..., help="File path to explain"),
    spec_dir: Path = typer.Option(
        Path("spec"),
        "--spec-dir",
        help="Path to spec directory",
    ),
):
    """
    Explain how a file maps to specifications.

    Shows traceability from generated files to spec sources
    (modules, deliverables, objectives).
    """
    spec_dir = spec_dir.resolve()

    if not spec_dir.exists():
        rprint(f"[red]Error:[/red] Spec directory not found: {spec_dir}")
        raise typer.Exit(1)

    try:
        loader = SpecLoader(spec_dir)
        orchestrator = AIOrchestrator(loader)

        explanation = orchestrator.explain(path)
        rprint(explanation)

    except Exception as e:
        rprint(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)


@ai_app.command("usage-prompt")
def ai_usage_prompt(
    plain: bool = typer.Option(
        False, "--plain", "-p", help="Output plain markdown without terminal formatting"
    ),
):
    """
    Generate comprehensive usage guide for AI assistants.

    Outputs a detailed, markdown-formatted guide explaining all workshopforge
    functionality. This prompt can be provided to AI assistants to help
    them understand and use workshopforge effectively.

    The guide includes:
    - Core principles (Spec-First, Session-Stability, Policy-Driven)
    - Workflow patterns (New Workshop, Iterative Enhancement, Troubleshooting)
    - Best practices for AI operations and goal planning
    - Common mistakes and how to avoid them
    - Provider selection guide
    - Advanced usage (custom templates, policies, CI/CD)
    - Debugging tips

    Examples:
        # Display the guide in terminal (formatted)
        workshopforge ai usage-prompt

        # Output plain markdown for files/clipboard
        workshopforge ai usage-prompt --plain

        # Save to file
        workshopforge ai usage-prompt --plain > .claude/ai-usage-prompt.md

        # Copy to clipboard (requires xclip/pbcopy)
        workshopforge ai usage-prompt --plain | xclip -selection clipboard
    """
    # Read the AI_USAGE_GUIDE.md from forge package
    guide_path = Path(__file__).parent / "AI_USAGE_GUIDE.md"

    if not guide_path.exists():
        rprint("[red]Error:[/red] AI_USAGE_GUIDE.md not found")
        raise typer.Exit(1)

    prompt = guide_path.read_text()

    if plain:
        # Output raw markdown for file/clipboard
        print(prompt)
    else:
        # Render as Markdown for beautiful terminal output
        md = Markdown(prompt)
        console.print(md)


if __name__ == "__main__":
    app()
