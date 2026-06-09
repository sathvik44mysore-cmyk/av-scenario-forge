# av-scenario-forge

> Formally verified safety-critical scenario generation for autonomous vehicles.

Natural language → **Nemotron 3** (parse) → **Fast Downward** (formal coverage verification) → **Scenic 3.0 script**

## Overview

AV safety testing requires thousands of scenarios covering specific safety properties. Most NL-to-scenario tools generate scripts directly from language — but they cannot *prove* a scenario actually covers the required properties. **av-scenario-forge adds a formal verification layer using PDDL planning**: before any script is generated, Fast Downward checks that every required safety property is reachable in the scenario. Gaps are automatically patched.

## Pipeline

```
Natural Language Description
          │
          ▼
┌─────────────────────┐
│   Nemotron 3 Super  │  ← NVIDIA NIM API
│   Scenario Parser   │
│   Extracts:         │
│   • safety props    │
│   • actors          │
│   • environment     │
│   • risk level      │
└──────────┬──────────┘
           │ structured scenario
           ▼
┌─────────────────────┐
│   Fast Downward     │  ← local PDDL planner
│   Coverage Verifier │
│                     │
│   Checks:           │
│   • all required    │
│     properties      │
│     reachable?      │
│   • flags gaps      │
└──────────┬──────────┘
           │ coverage report + gaps
           ▼
┌─────────────────────┐
│   Nemotron 3 Super  │  ← NVIDIA NIM API
│   Scenic Generator  │
│                     │
│   Outputs:          │
│   • Scenic 3.0 code │
│   • patches gaps    │
│   • plain summary   │
└─────────────────────┘
```

## Stack

| Component | Tool |
|---|---|
| Scenario parsing + script generation | Nemotron 3 Super (NVIDIA NIM API) |
| Formal coverage verification | Fast Downward (PDDL planner) |
| Simulation runtime | CARLA / any Scenic-compatible simulator |

## Setup

```bash
pip install openai

# Get a free API key at build.nvidia.com
export NIM_API_KEY=your_key_here
```

Fast Downward must be installed locally:
```bash
git clone https://github.com/aibasel/downward.git ~/fast_downward
cd ~/fast_downward && python3 build.py
```

## Usage

```bash
# Basic usage
python3 -m src.forge "A child runs onto a highway at night during heavy rain"

# Specify required safety properties (formal verification checks these)
python3 -m src.forge \
  --required "emergency_vehicle,sudden_braking,intersection,night_driving" \
  "An ambulance runs a red light at a junction"

# Save Scenic script to file
python3 -m src.forge "Truck cuts in suddenly on motorway" --output scenario.scenic
```

## Example Output

```
Input: "An ambulance runs a red light at a junction"
Required: emergency_vehicle, sudden_braking, intersection, night_driving

[1/3] Nemotron 3: parsing scenario...
      Title:      Ambulance runs red light at junction
      Properties: ['emergency_vehicle', 'intersection']
      Risk level: high

[2/3] Fast Downward: verifying safety coverage...
      Coverage:   50.0%
      Covered:    ['emergency_vehicle', 'intersection']
      MISSING:    ['night_driving', 'sudden_braking']  ← will be patched
      PDDL valid: True

[3/3] Nemotron 3: generating Scenic 3.0 script...
      Patched:    ['night_driving', 'sudden_braking']

      Summary: An ambulance proceeds through a red-light at a junction while the
      autonomous vehicle is approaching. The scenario is set at night and forces
      the AV to execute sudden braking to avoid a collision.
```

See [`examples/`](examples/) for full Scenic 3.0 scripts from real pipeline runs.

## Safety Properties Catalogue

25 tracked properties across 6 categories:

| Category | Properties |
|---|---|
| Visibility | `night_driving`, `fog`, `glare_sun` |
| Weather / Road | `rain`, `snow`, `wet_road`, `icy_road` |
| Actors | `pedestrian_crossing`, `cyclist_present`, `child_present`, `emergency_vehicle`, `truck_or_bus`, `motorcycle` |
| Maneuvers | `sudden_cut_in`, `sudden_braking`, `lane_merge` |
| Infrastructure | `construction_zone`, `intersection`, `narrow_lane`, `road_works`, `parked_vehicles_blocking` |
| Speed regime | `highway_speed`, `urban_low_speed`, `traffic_jam` |

## Author

Sathvik Lokesh — M.Sc. Information Technology, University of Stuttgart
