# av-scenario-forge

> Formally verified safety-critical scenario generation for autonomous vehicles.

Natural language → **Nemotron 3** (parse) → **Fast Downward** (formal coverage verification) → **Scenic 3.0 script**

## Why this exists

AV companies like Waymo, Mobileye, and Bosch need thousands of safety-critical test scenarios. Tools like SaferDrive AI generate them from natural language — but they can't *prove* a scenario covers the required safety properties. **av-scenario-forge adds formal verification using PDDL planning**, ensuring every required property is reachable before a single simulation runs.

## Pipeline

```
Natural Language Description
          │
          ▼
┌─────────────────────┐
│   Nemotron 3 Super  │  ← NVIDIA NIM API (free)
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
│   Fast Downward     │  ← local (no GPU needed)
│   PDDL Verifier     │
│                     │
│   Checks:           │
│   • all required    │
│     properties      │
│     covered?        │
│   • flags gaps      │
└──────────┬──────────┘
           │ coverage report + gaps
           ▼
┌─────────────────────┐
│   Nemotron 3 Super  │  ← NVIDIA NIM API (free)
│   Scenic Generator  │
│                     │
│   Outputs:          │
│   • Scenic 3.0 code │
│   • patches gaps    │
│   • plain summary   │
└─────────────────────┘
```

## Free Stack

| Component | Tool | Cost |
|---|---|---|
| Scenario parsing + script generation | Nemotron 3 Super (NIM API) | **Free** |
| Formal coverage verification | Fast Downward (PDDL) | **Free** |
| Simulation runtime | CARLA (optional) | **Free** |

## Setup

```bash
pip install openai
export NIM_API_KEY=your_key_here   # free at build.nvidia.com
```

## Usage

```bash
cd ~/Hanuman/nvidia-target/av-scenario-forge

# Basic usage
python3 -m src.forge "A child runs onto a highway at night during heavy rain"

# Specify required safety properties
python3 -m src.forge \
  --required "night_driving,pedestrian_crossing,rain,sudden_braking" \
  "A pedestrian steps off the pavement at an unlit intersection during fog"

# Save Scenic script
python3 -m src.forge "Truck cuts in suddenly on motorway" --output scenario.scenic
```

## Example Output

```
[1/3] Nemotron 3: parsing scenario...
      Title:      Night Rain Pedestrian Crossing
      Properties: ['night_driving', 'rain', 'wet_road', 'pedestrian_crossing', 'child_present']
      Risk level: critical

[2/3] Fast Downward: verifying safety coverage...
      Coverage:   80.0%
      Covered:    ['night_driving', 'pedestrian_crossing', 'rain', 'wet_road']
      MISSING:    ['sudden_braking']  ← will be patched
      PDDL valid: True

[3/3] Nemotron 3: generating Scenic 3.0 script...
      Patched:    ['sudden_braking']
      Summary: A child pedestrian crosses a wet road at night in rain...
```

## Safety Properties Catalogue

25 tracked properties across 6 categories:
- **Visibility:** night_driving, fog, glare_sun
- **Weather/Road:** rain, snow, wet_road, icy_road
- **Actors:** pedestrian_crossing, cyclist_present, child_present, emergency_vehicle, truck_or_bus
- **Maneuvers:** sudden_cut_in, sudden_braking, lane_merge
- **Infrastructure:** construction_zone, intersection, narrow_lane, road_works
- **Speed regime:** highway_speed, urban_low_speed, traffic_jam

## Author

Sathvik — Master's student, University of Stuttgart  
Targeting NVIDIA DRIVE, Bosch AI, Continental, Mobileye.
