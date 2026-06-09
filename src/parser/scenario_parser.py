"""
Step 1 — Nemotron 3 parses a natural language scenario description into a
structured dict of safety properties, actors, and environment conditions.
"""

import json
import re
from src.utils.nim_client import NIMClient

_SYSTEM = (
    "You are an autonomous vehicle safety engineer. "
    "Parse driving scenarios into structured safety properties used for AV test coverage. "
    "Always respond in valid JSON only."
)

# Full catalogue of safety properties the system tracks
SAFETY_PROPERTIES = [
    "night_driving", "rain", "fog", "snow", "glare_sun",
    "wet_road", "icy_road", "construction_zone",
    "pedestrian_crossing", "cyclist_present", "child_present",
    "emergency_vehicle", "truck_or_bus", "motorcycle",
    "highway_speed", "urban_low_speed", "intersection",
    "lane_merge", "sudden_cut_in", "sudden_braking",
    "traffic_jam", "road_works", "narrow_lane",
    "parked_vehicles_blocking", "animal_on_road",
]


class ScenarioParser:
    def __init__(self, nim_client: NIMClient):
        self.client = nim_client

    def parse(self, nl_description: str) -> dict:
        """
        Parse NL scenario description into structured form.

        Returns:
        {
            "title": str,
            "description": str,
            "safety_properties": [str, ...],   # from SAFETY_PROPERTIES catalogue
            "actors": [{"type": str, "behavior": str}, ...],
            "environment": {"time_of_day": str, "weather": str, "road_type": str},
            "ego_speed_kmh": int,
            "risk_level": "low"|"medium"|"high"|"critical"
        }
        """
        prompt = (
            f'Parse this AV test scenario:\n"{nl_description}"\n\n'
            f"Safety property catalogue: {SAFETY_PROPERTIES}\n\n"
            "Return JSON only:\n"
            '{\n'
            '  "title": str,\n'
            '  "description": str,\n'
            '  "safety_properties": [only values from catalogue that apply],\n'
            '  "actors": [{"type": str, "behavior": str}],\n'
            '  "environment": {"time_of_day": str, "weather": str, "road_type": str},\n'
            '  "ego_speed_kmh": int,\n'
            '  "risk_level": "low"|"medium"|"high"|"critical"\n'
            '}'
        )
        raw = self.client.chat(
            messages=[{"role": "system", "content": _SYSTEM},
                      {"role": "user", "content": prompt}],
            temperature=0.1,
            max_tokens=2048,
        )
        return self._parse_json(raw)

    def _parse_json(self, raw: str) -> dict:
        # Strip markdown fences
        cleaned = re.sub(r'```[a-zA-Z]*', '', raw).strip().strip('`').strip()
        # Remove inline comments (// ...) that Nemotron sometimes adds
        cleaned = re.sub(r'//[^\n]*', '', cleaned)
        # Remove trailing commas before } or ]
        cleaned = re.sub(r',\s*([\}\]])', r'\1', cleaned)
        try:
            return json.loads(cleaned)
        except json.JSONDecodeError:
            match = re.search(r'\{.*\}', cleaned, re.DOTALL)
            if match:
                try:
                    return json.loads(match.group())
                except json.JSONDecodeError:
                    pass
            print(f"[Parser] raw response:\n{raw}")
            raise ValueError(f"Could not parse JSON from Nemotron response")
