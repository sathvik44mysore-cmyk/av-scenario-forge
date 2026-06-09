"""
Step 3 — Nemotron 3 generates a Scenic 3.0 simulation script from the
formally verified scenario. Scenic is the industry-standard probabilistic
programming language for AV scenario specification (used by Waymo, NVIDIA DRIVE,
CARLA, and academic AV safety research).

If coverage gaps were found in Step 2, Nemotron is instructed to patch them
before generating the script.
"""

import re
from src.utils.nim_client import NIMClient

_SYSTEM = (
    "You are an autonomous vehicle simulation engineer with expertise in Scenic 3.0 "
    "(the probabilistic programming language for AV scenarios) and OpenSCENARIO 2.0. "
    "Generate realistic, safety-critical simulation scripts for AV testing."
)


class ScenicGenerator:
    def __init__(self, nim_client: NIMClient):
        self.client = nim_client

    def generate(self, scenario: dict, coverage_result: dict) -> dict:
        """
        Generate a Scenic 3.0 script for the verified scenario.
        If coverage_result has missing properties, patch them into the script.

        Returns:
        {
            "scenic_script": str,          # full Scenic 3.0 code
            "patched_properties": [str],   # missing properties that were added
            "scenario_summary": str        # plain English summary
        }
        """
        missing   = coverage_result.get("missing", [])
        patch_note = ""
        if missing:
            patch_note = (
                f"\nIMPORTANT: The scenario is missing these required safety properties: {missing}. "
                "You MUST include them in the generated script.\n"
            )

        prompt = (
            f"Write a Scenic 3.0 script for this AV test scenario.\n\n"
            f"Title: {scenario['title']}\n"
            f"Safety properties: {scenario['safety_properties']}\n"
            f"Actors: {scenario['actors']}\n"
            f"Environment: {scenario['environment']}\n"
            f"Ego speed: {scenario.get('ego_speed_kmh', 60)} km/h\n"
            f"{patch_note}\n"
            "Rules:\n"
            "- Start immediately with the code — no explanations, no reasoning\n"
            "- First line must be a # comment describing the scenario\n"
            "- Use Scenic 3.0 syntax: param, ego = new Car, new Pedestrian, behavior, require\n"
            "- Include Range() or Normal() for probabilistic variation\n"
            "- Set map = 'Town03.xodr' for CARLA\n"
            "- End with require statements for safety constraints\n"
            "- Output raw code only — no markdown fences, no prose"
        )
        raw_script = self.client.chat(
            messages=[{"role": "system", "content": _SYSTEM},
                      {"role": "user", "content": prompt}],
            temperature=0.2,
            max_tokens=3500,
        )
        scenic_script = self._extract_code(raw_script)

        summary = self._generate_summary(scenario, missing)

        return {
            "scenic_script":      scenic_script,
            "patched_properties": missing,
            "scenario_summary":   summary,
        }

    def _generate_summary(self, scenario: dict, patched: list[str]) -> str:
        patch_note = f" (added missing properties: {patched})" if patched else ""
        prompt = (
            f"Summarise this AV test scenario in 2 sentences for a safety engineer:\n"
            f"Title: {scenario['title']}\n"
            f"Properties: {scenario['safety_properties']}\n"
            f"Risk: {scenario.get('risk_level', 'high')}{patch_note}"
        )
        return self.client.chat(
            messages=[{"role": "system", "content": _SYSTEM},
                      {"role": "user", "content": prompt}],
            temperature=0.3,
            max_tokens=300,
        )

    def _extract_code(self, raw: str) -> str:
        # If model wrapped in fences, extract just the code block
        fence_match = re.search(r'```(?:python|scenic)?\n(.*?)```', raw, re.DOTALL)
        if fence_match:
            return fence_match.group(1).strip()

        # Nemotron 3 Super is a reasoning model — it sometimes thinks out loud before
        # outputting code. Find where the actual code starts (first # comment or keyword).
        code_start = re.search(
            r'^(#|param |ego |from |import |map |timeOfDay |weather )',
            raw, re.MULTILINE
        )
        if code_start:
            return raw[code_start.start():].strip()

        # Fallback: return everything stripped of obvious prose lines
        lines = raw.splitlines()
        code_lines = [l for l in lines if not re.match(
            r'^(We |Let |I |The |Note |This |Thus |Here |Now |So |Then |Actually |But )', l
        )]
        return "\n".join(code_lines).strip()
