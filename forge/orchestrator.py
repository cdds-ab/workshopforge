"""
AI orchestrator for workshop generation and adaptation.

Manages the plan/apply pipeline: generates plans from user goals,
validates against policies, and executes changes with full logging.
"""

import json
import shutil
from pathlib import Path
from typing import Any, Dict, List, Optional

from .loader import SpecLoader
from .policies import PolicyEngine, PolicyViolation
from .prelude import PreludeGenerator
from .providers import get_provider
from .reporters import ComplianceReporter, format_plan_report
from .utils import compute_hash, ensure_dir, timestamp, write_json


class AIOrchestrator:
    """
    Orchestrates AI-driven workshop generation with policy enforcement.

    Implements the plan/apply/check/explain pipeline with full auditability
    through persistent logging and state tracking.
    """

    def __init__(
        self,
        spec_loader: SpecLoader,
        provider_name: str = "echo",
        state_dir: Optional[Path] = None,
    ):
        """
        Initialize orchestrator.

        Args:
            spec_loader: Loaded specifications
            provider_name: AI provider to use (echo, openai, anthropic)
            state_dir: Directory for state and logs (default: .workshopforge)
        """
        self.loader = spec_loader
        self.provider = get_provider(provider_name)
        self.prelude_gen = PreludeGenerator(spec_loader)
        self.policy_engine = PolicyEngine()

        # Set up state directory
        if state_dir is None:
            spec_dir = Path(spec_loader.spec_dir)
            state_dir = spec_dir.parent / ".workshopforge"
        self.state_dir = ensure_dir(state_dir)

        # Directories for logging and reports
        self.logs_dir = ensure_dir(self.state_dir.parent / "ai_logs")
        self.reports_dir = ensure_dir(self.state_dir.parent / "reports")

    def plan(self, user_goal: str) -> Dict[str, Any]:
        """
        Generate a plan from user goal without making changes.

        Args:
            user_goal: User's stated objective

        Returns:
            Plan dictionary with keys: goal, rationale, steps, risks, spec_hash
        """
        # Generate prelude
        prelude_text = self.prelude_gen.generate()
        spec_hash = self.prelude_gen.get_hash()

        # Build messages for AI
        messages = self.prelude_gen.build_messages(user_goal)

        # Get plan from provider
        response = self.provider.complete(messages)

        # Parse response into structured plan
        # (In production, would have structured prompting/parsing)
        plan = {
            "goal": user_goal,
            "spec_hash": spec_hash,
            "provider": self.provider.get_name(),
            "generated_at": timestamp(),
            "rationale": "See response text",
            "steps": [{"description": "See response text", "affected_files": []}],
            "risks": ["Verify spec compliance before applying"],
            "response_text": response,
        }

        # Log plan
        self._log_operation("plan", user_goal, prelude_text, response, plan)

        return plan

    def apply(
        self,
        user_goal: str,
        allow_violations: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """
        Execute plan: generate content, validate, and write if compliant.

        Args:
            user_goal: User's stated objective
            allow_violations: List of rule IDs to ignore (e.g., ["naming-convention"])

        Returns:
            Result dictionary with keys: success, violations, changes

        Raises:
            RuntimeError: If spec hash changed or critical errors occur
        """
        # Generate plan first
        plan = self.plan(user_goal)

        # Check if spec hash matches previous state
        self._verify_spec_stability(plan["spec_hash"])

        # For echo provider, simulate changes (in production, AI generates actual content)
        changes = self._simulate_changes(user_goal)

        # Run policy checks (for now, on current state)
        # In full implementation, would check staged changes
        target_dir = self.loader.spec_dir.parent / "out" / "instructor"
        violations = self.policy_engine.check(self.loader, target_dir if target_dir.exists() else None)

        # Filter allowed violations
        if allow_violations:
            violations = self.policy_engine.filter_allowed(violations, allow_violations)

        # Check for blocking errors
        has_errors = self.policy_engine.has_errors(violations)

        result = {
            "success": not has_errors,
            "goal": user_goal,
            "spec_hash": plan["spec_hash"],
            "provider": plan["provider"],
            "applied_at": timestamp(),
            "changes": changes,
            "violations": [v.to_dict() for v in violations],
        }

        # Write changes only if no errors
        if not has_errors:
            self._apply_changes(changes)
            result["message"] = f"Applied {len(changes)} changes successfully"
        else:
            result["message"] = f"Blocked by {len([v for v in violations if v.severity == 'error'])} policy errors"

        # Generate compliance report
        reporter = ComplianceReporter(self.reports_dir)
        reporter.generate_reports(violations)

        # Log apply operation
        self._log_apply(user_goal, plan, result)

        # Update state
        self._update_state(plan["spec_hash"], plan["provider"], user_goal)

        return result

    def check(self, target_dir: Optional[Path] = None) -> List[PolicyViolation]:
        """
        Run compliance checks on workshop without making changes.

        Args:
            target_dir: Workshop directory to check (optional)

        Returns:
            List of policy violations
        """
        violations = self.policy_engine.check(self.loader, target_dir)

        # Generate reports
        reporter = ComplianceReporter(self.reports_dir)
        reporter.generate_reports(violations)

        return violations

    def explain(self, file_path: str) -> str:
        """
        Explain how a file maps to specifications.

        Args:
            file_path: Path to file to explain

        Returns:
            Explanation text with spec references
        """
        path = Path(file_path)
        explanations = []

        # Check if file is a deliverable
        modules = self.loader.get_modules()
        for module in modules:
            deliverables = module.get("deliverables", [])
            if file_path in deliverables or str(path.name) in [Path(d).name for d in deliverables]:
                explanations.append(
                    f"- Deliverable for module `{module['id']}` (modules.yml#{module['id']})\n"
                    f"  Objective: {module['objective']}"
                )

        # Check if in instructor/reference
        if "instructor" in path.parts:
            explanations.append("- Part of instructor-only materials (not for students)")
        if "reference" in path.parts:
            explanations.append("- Reference solution (instructor access only)")

        # Check if in labs
        if "labs" in path.parts:
            explanations.append("- Student-facing lab exercise")

        if not explanations:
            return f"File `{file_path}` is not directly referenced in specifications."

        result = f"# File: {file_path}\n\n## Spec References\n\n"
        result += "\n".join(explanations)
        return result

    def _simulate_changes(self, goal: str) -> List[Dict[str, Any]]:
        """
        Simulate file changes for echo provider.

        In production, AI would generate actual content.
        """
        return [
            {
                "path": "example/generated-file.md",
                "action": "create",
                "description": f"Generated for goal: {goal}",
            }
        ]

    def _apply_changes(self, changes: List[Dict[str, Any]]) -> None:
        """
        Write changes to filesystem.

        Args:
            changes: List of change dicts with path, action, content
        """
        for change in changes:
            path = Path(change["path"])
            action = change["action"]

            if action == "create":
                ensure_dir(path.parent)
                path.write_text(
                    change.get("content", f"# Generated content\n\nGoal: {change.get('description')}"),
                    encoding="utf-8",
                )

    def _log_operation(
        self,
        operation: str,
        goal: str,
        prelude: str,
        response: str,
        plan: Dict[str, Any],
    ) -> Path:
        """
        Log AI operation to timestamped directory.

        Args:
            operation: Operation type (plan, apply)
            goal: User goal
            prelude: Prelude text
            response: AI response
            plan: Plan dictionary

        Returns:
            Path to log directory
        """
        from .utils import safe_filename

        # Create timestamped log directory
        timestamp_str = timestamp().replace(":", "-").replace(".", "-")
        goal_slug = safe_filename(goal[:30])
        log_dir = ensure_dir(self.logs_dir / f"{timestamp_str}-{goal_slug}")

        # Write log files
        (log_dir / "prelude.txt").write_text(prelude, encoding="utf-8")
        (log_dir / "prompt.json").write_text(
            json.dumps({"goal": goal, "operation": operation}, indent=2),
            encoding="utf-8",
        )
        (log_dir / "response.txt").write_text(response, encoding="utf-8")
        write_json(log_dir / "plan.json", plan)

        # Write formatted plan
        if operation == "plan":
            plan_md = format_plan_report(plan)
            (log_dir / "plan.md").write_text(plan_md, encoding="utf-8")

        return log_dir

    def _log_apply(self, goal: str, plan: Dict[str, Any], result: Dict[str, Any]) -> None:
        """Log apply operation results."""
        # Find most recent log dir for this goal
        # For simplicity, create new log entry
        self._log_operation("apply", goal, "", result.get("message", ""), result)

    def _verify_spec_stability(self, expected_hash: str) -> None:
        """
        Verify spec hash hasn't changed since last operation.

        Args:
            expected_hash: Expected spec hash

        Raises:
            RuntimeError: If hash mismatch detected
        """
        state = self._load_state()
        if state and state.get("spec_hash") != expected_hash:
            raise RuntimeError(
                "Spec hash changed since last operation. "
                "Specifications were modified. Re-run plan to update."
            )

    def _load_state(self) -> Optional[Dict[str, Any]]:
        """Load orchestrator state."""
        state_file = self.state_dir / "state.json"
        if not state_file.exists():
            return None

        with open(state_file, "r") as f:
            return json.load(f)

    def _update_state(self, spec_hash: str, provider: str, last_goal: str) -> None:
        """Update orchestrator state."""
        state = {
            "spec_hash": spec_hash,
            "provider": provider,
            "last_goal": last_goal,
            "updated_at": timestamp(),
        }

        state_file = self.state_dir / "state.json"
        write_json(state_file, state)
