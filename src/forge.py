"""
av-scenario-forge — main pipeline.

Usage:
    python3 -m src.forge "A child runs onto a highway at night during heavy rain"
    python3 -m src.forge --required night_driving,pedestrian_crossing,rain "..."
"""

import argparse
import json
import sys
from src.utils.nim_client import NIMClient
from src.parser.scenario_parser import ScenarioParser, SAFETY_PROPERTIES
from src.verifier.coverage_checker import CoverageChecker
from src.generator.scenic_generator import ScenicGenerator

# Default required properties for a comprehensive AV safety test suite
DEFAULT_REQUIRED = [
    "night_driving",
    "pedestrian_crossing",
    "wet_road",
    "sudden_braking",
    "intersection",
]


def run(nl_description: str, required_properties: list[str] = None) -> dict:
    required = required_properties or DEFAULT_REQUIRED
    nim = NIMClient()

    print("\n[1/3] Nemotron 3: parsing scenario...")
    scenario = ScenarioParser(nim).parse(nl_description)
    print(f"      Title:      {scenario['title']}")
    print(f"      Properties: {scenario['safety_properties']}")
    print(f"      Risk level: {scenario['risk_level']}")

    print("\n[2/3] Fast Downward: verifying safety coverage...")
    coverage = CoverageChecker().check(scenario, required)
    print(f"      Coverage:   {coverage['coverage_pct']}%")
    print(f"      Covered:    {coverage['covered']}")
    if coverage["missing"]:
        print(f"      MISSING:    {coverage['missing']}  ← will be patched")
    print(f"      PDDL valid: {coverage['pddl_verified']}")

    print("\n[3/3] Nemotron 3: generating Scenic 3.0 script...")
    output = ScenicGenerator(nim).generate(scenario, coverage)
    if output["patched_properties"]:
        print(f"      Patched:    {output['patched_properties']}")
    print(f"\n      Summary: {output['scenario_summary']}")

    return {
        "scenario":  scenario,
        "coverage":  coverage,
        "scenic":    output["scenic_script"],
        "summary":   output["scenario_summary"],
    }


def main():
    parser = argparse.ArgumentParser(description="AV Safety Scenario Forge")
    parser.add_argument("description", help="Natural language scenario description")
    parser.add_argument("--required", default="",
                        help="Comma-separated required safety properties")
    parser.add_argument("--output", default=None, help="Save Scenic script to file")
    args = parser.parse_args()

    required = [p.strip() for p in args.required.split(",") if p.strip()] or None
    result = run(args.description, required)

    print("\n" + "="*60)
    print("SCENIC 3.0 SCRIPT")
    print("="*60)
    print(result["scenic"])

    if args.output:
        with open(args.output, "w") as f:
            f.write(result["scenic"])
        print(f"\nScript saved to {args.output}")


if __name__ == "__main__":
    main()
