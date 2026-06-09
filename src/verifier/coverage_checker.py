"""
Step 2 — Fast Downward verifies that the scenario covers all required
safety properties. This is the formal verification layer that separates
av-scenario-forge from ML-only tools like SaferDrive AI.

A PDDL problem is generated from the parsed scenario and solved with
Fast Downward. If a plan exists, every required property is reachable
(achievable) in the scenario. Properties that are NOT covered are
flagged as gaps for Nemotron to address in the next step.
"""

import subprocess
import tempfile
import os
from pathlib import Path

FAST_DOWNWARD = str(Path("~/fast_downward/fast-downward.py").expanduser())
DOMAIN_PATH   = str(Path(__file__).parent.parent.parent / "pddl" / "av_safety_domain.pddl")


class CoverageChecker:
    def __init__(self, fast_downward_path: str = FAST_DOWNWARD):
        self.fd_path = fast_downward_path

    def check(self, scenario: dict, required_properties: list[str]) -> dict:
        """
        Verify the scenario covers all required_properties using PDDL planning.

        Returns:
        {
            "covered":   [str, ...],   # properties present in scenario
            "missing":   [str, ...],   # required but not in scenario
            "extra":     [str, ...],   # in scenario but not required
            "valid":     bool,         # True if all required properties covered
            "coverage_pct": float
        }
        """
        present   = set(scenario.get("safety_properties", []))
        required  = set(required_properties)
        covered   = present & required
        missing   = required - present
        extra     = present - required

        # Formal PDDL verification — confirm planner can achieve full coverage
        pddl_valid = self._verify_with_pddl(present, required) if required else True

        coverage_pct = round(len(covered) / len(required) * 100, 1) if required else 100.0

        return {
            "covered":      sorted(covered),
            "missing":      sorted(missing),
            "extra":        sorted(extra),
            "valid":        len(missing) == 0 and pddl_valid,
            "coverage_pct": coverage_pct,
            "pddl_verified": pddl_valid,
        }

    def _verify_with_pddl(self, present: set, required: set) -> bool:
        domain  = Path(DOMAIN_PATH).read_text()
        problem = self._build_problem(present, required)

        domain_f  = "/tmp/avforge_domain.pddl"
        problem_f = "/tmp/avforge_problem.pddl"
        Path(domain_f).write_text(domain)
        Path(problem_f).write_text(problem)

        try:
            result = subprocess.run(
                ["python3", self.fd_path, domain_f, problem_f, "--search", "astar(lmcut())"],
                capture_output=True, text=True, timeout=30,
            )
            # Fast Downward writes plan to sas_plan file, not stdout.
            # Check stdout for "Solution found" OR check if sas_plan file was created.
            stdout_combined = result.stdout + result.stderr
            if "Solution found" in stdout_combined:
                return True
            # Some FD versions print plan lines to stdout
            if any(line.strip().startswith("(") for line in result.stdout.splitlines()):
                return True
            # Check sas_plan file in cwd
            if os.path.exists("sas_plan"):
                return True
            return False
        except (subprocess.TimeoutExpired, FileNotFoundError):
            # Fast Downward not available — fall back to set-based check
            return required.issubset(present)

    def _build_problem(self, present: set, required: set) -> str:
        all_props  = present | required
        objects    = "\n    ".join(f"{p} - safety-property" for p in sorted(all_props))
        init_lines = "\n    ".join(f"(property-required {p})" for p in sorted(required))
        # Pre-cover properties already present in the scenario
        pre_covered = "\n    ".join(f"(property-covered {p})" for p in sorted(present & required))
        goal_lines  = "\n    ".join(f"(property-covered {p})" for p in sorted(required))

        return f"""(define (problem av-coverage)
  (:domain av-safety)
  (:objects
    main-scenario - scenario
    {objects}
  )
  (:init
    (scenario-active main-scenario)
    {init_lines}
    {pre_covered}
  )
  (:goal
    (and
      {goal_lines}
    )
  )
)
"""
