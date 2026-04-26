# Gaming, VFX & Metaverse — Avatar Generation & Engine Integration

<br>

## Business Context

**The Problem:** A height slider doesn't create a personalized avatar — it just stretches a generic mesh. The underlying skeletal proportions were authored by eye, not measured, which is why your technical artists spend a disproportionate share of their time fixing deformation in the same joints (shoulders, hips, knees, wrists) on every character variant. And when design asks for 50 NPC body variants for an open-world crowd, you're either spending art days per variant or shipping obvious clones.

**The Solution:** You need height and weight. DimensionsPot takes those two inputs and returns a complete, 130-point anthropometric profile in under 10ms. You get exact bone lengths to drive the skeletal rig, and precise circumferences to control the blend shapes. Players building their own avatar get a character that actually matches their physical body — their shoulder breadth, their torso-to-leg ratio, their real build. Not a stretched default.

**The Crowd Multiplier:** For open-world games and VFX, populating backgrounds with diverse, realistic bodies is a resource sink. DimensionsPot lets you generate statistically accurate NPCs programmatically. By adjusting `target_region` and `body_build_type`, you spawn a crowd with accurate Asian skeletal proportions or European civilian body fat distributions in a scripting loop — no manual modeling required.

<br>

## Recommended API Configuration

| Parameter | Value | Reason |
|---|---|---|
| `anchors` | `body_height` + `body_mass` | PRIMARY_BOTH tier; all skeletal BONE dims at confidence ~85 |
| `body_build_type` | `CIVILIAN` / `ATHLETIC` / `OVERWEIGHT` | Match character archetype |
| `bundle` | `FULL_BODY` | Avatar rigs require the complete skeletal and soft-tissue profile |
| `target_region` | Character's population origin | Ensures regionally accurate skeletal proportions |
| `confidence_score_threshold` | `0` | Include all dimensions; engine ensures internal proportion consistency |
| `include_range_95` | `false` | Not needed for rigging; reduces payload |
| `include_iso_codes` | `false` | Not needed for rigging |

<br>

### Dimension categories for avatar rigging:

| Rig Component | Key Dimensions | Type |
|---|---|---|
| Spine / torso height | `sitting_height`, `shoulder_height`, `cervicale_height` | BONE |
| Shoulder width | `biacromial_breadth`, `shoulder_breadth` | BONE |
| Arm proportions | `upper_arm_length`, `forearm_length`, `arm_length_total` | BONE |
| Hand detail | `hand_length`, `palm_length`, all `hand_digit_*` lengths and widths | BONE |
| Hip / pelvis | `hip_breadth_bicristal`, `trochanterion_height` | BONE |
| Leg proportions | `inseam_length`, `crotch_height`, `knee_height`, `popliteal_height` | BONE |
| Head / face | `head_breadth`, `head_length`, `bizygomatic_breadth`, `face_length` | BONE |
| Soft tissue volumes | `chest_circumference`, `waist_circumference_natural`, `hip_circumference`, `hip_breadth`, `thigh_circumference` | FLESH |
| Foot | `foot_length`, `foot_breadth`, `ankle_height` | BONE |

<br>

## Sample Request — User Self-Avatar (ASIA_PACIFIC, male)

```bash
curl -X POST "https://dimensionspot.p.rapidapi.com/v1/predict" \
  -H "Content-Type: application/json" \
  -H "X-RapidAPI-Key: YOUR_API_KEY" \
  -H "X-RapidAPI-Host: dimensionspot.p.rapidapi.com" \
  -d '{
    "input_data": {
      "input_unit_system": "metric",
      "subject": {
        "gender": "male",
        "exact_age": 26.0,
        "age_category": "ADULT",
        "input_origin_region": "ASIA_PACIFIC"
      },
      "anchors": {
        "body_height": 1750.0,
        "body_mass": 70.0
      }
    },
    "output_settings": {
      "calculation": {
        "calculation_model": "AUTO",
        "target_region": "ASIA_PACIFIC",
        "body_build_type": "CIVILIAN"
      },
      "requested_dimensions": {
        "bundle": "FULL_BODY",
        "specific_dimensions": null
      },
      "output_format": {
        "unit_system": "metric",
        "confidence_score_threshold": 0,
        "include_range_95": false,
        "include_iso_codes": false
      }
    }
  }'
```

<br>

## Unity Humanoid Rig — Bone Mapping

Unity's Humanoid rig uses bone lengths in metres. Extract and convert from the API response:

```csharp
// C# — extract dimensions from DimensionsPot response JSON
// All API values are in mm; multiply by 0.001 to convert to metres.
float MM_TO_M = 0.001f;

float upperArmLength    = dims["upper_arm_length"]["value"]        * MM_TO_M;
float forearmLength     = dims["forearm_length"]["value"]           * MM_TO_M;
float handLength        = dims["hand_length"]["value"]              * MM_TO_M;

// Derived leg segment lengths from standing heights:
//   upper leg (femur) = trochanterion_height − knee_height
//   lower leg (tibia) = knee_height − ankle_height
float upperLegLength    = (dims["trochanterion_height"]["value"]
                          - dims["knee_height"]["value"])           * MM_TO_M;
float lowerLegLength    = (dims["knee_height"]["value"]
                          - dims["ankle_height"]["value"])          * MM_TO_M;

float spineHeight       = dims["sitting_height"]["value"]           * MM_TO_M;
float shoulderWidth     = dims["biacromial_breadth"]["value"]       * MM_TO_M;
float headCircumference = dims["head_circumference"]["value"]       * MM_TO_M;

// Apply to Avatar configuration via AvatarBuilder or runtime rig adjustment
```

> `BONE` dimensions (limb lengths, breadths, skeletal heights) map directly to rig bone lengths. `FLESH` dimensions (circumferences) drive blend shape weights and clothing simulation mesh targets.

<br>

## Unreal MetaHuman — Blend Shape Driving

Map DimensionsPot circumference dimensions to MetaHuman body shape parameters (normalised 0.0–1.0). Use anatomically plausible population ranges as normalisation bounds — not the biological limit extremes:

```python
# Python — map API dims to MetaHuman body shape parameters

def normalize(value_mm, min_mm, max_mm):
    """Clamp-normalise to [0.0, 1.0]."""
    return max(0.0, min(1.0, (value_mm - min_mm) / (max_mm - min_mm)))

dims = response["body_dimensions"]

metahuman_params = {
    # Chest: 800 mm (slim civilian) to 1400 mm (heavy build)
    "chest_width":    normalize(dims["chest_circumference"]["value"], 800, 1400),
    # Waist: 600 mm to 1200 mm
    "waist_width":    normalize(dims["waist_circumference_natural"]["value"], 600, 1200),
    # Hip: 700 mm to 1400 mm
    "hip_width":      normalize(dims["hip_circumference"]["value"], 700, 1400),
    # Shoulder (bony breadth): 320 mm to 520 mm
    "shoulder_width": normalize(dims["biacromial_breadth"]["value"], 320, 520),
    # Leg length (inseam): 700 mm to 1050 mm
    "leg_length":     normalize(dims["inseam_length"]["value"], 700, 1050),
    # Thigh girth: 400 mm to 800 mm
    "thigh_girth":    normalize(dims["thigh_circumference"]["value"], 400, 800),
}
```

<br>

## Finger Rig Mapping

DimensionsPot provides per-digit lengths and joint widths for all 5 fingers, derived via validated Greiner anatomical ratio models from `hand_length`:

```python
finger_map = {
    "thumb":  {"length": "hand_digit_1_length", "ip_width":  "hand_digit_1_width_ip"},
    "index":  {"length": "hand_digit_2_length", "pip": "hand_digit_2_width_pip", "dip": "hand_digit_2_width_dip"},
    "middle": {"length": "hand_digit_3_length", "pip": "hand_digit_3_width_pip", "dip": "hand_digit_3_width_dip"},
    "ring":   {"length": "hand_digit_4_length", "pip": "hand_digit_4_width_pip", "dip": "hand_digit_4_width_dip"},
    "pinky":  {"length": "hand_digit_5_length", "pip": "hand_digit_5_width_pip", "dip": "hand_digit_5_width_dip"},
}

for finger, keys in finger_map.items():
    length_m = dims[keys["length"]]["value"] * 0.001
    print(f"{finger}: {length_m:.4f}m")
```

> Digit widths are derived via Greiner ratio scaling from `hand_length` and carry a −10% confidence adjustment. They are sufficient for mesh deformation and animation rigging; for high-fidelity haptic glove fitting, prefer direct measurement.

<br>

## NPC / Crowd Generation Pattern

Generate statistically realistic body profiles for a target demographic. Vary `body_mass` within a plausible range for a fixed height to produce natural body composition variation:

```python
import random

def generate_npc_profile(gender, height_mm, target_region, body_build_type="CIVILIAN"):
    """
    Generate a single NPC body profile.
    Vary body_mass around a population-typical value for the given height.
    """
    # BMI range: 18.5–30 for CIVILIAN, 22–28 for ATHLETIC
    bmi_range = (22, 28) if body_build_type == "ATHLETIC" else (19, 29)
    height_m = height_mm / 1000
    bmi = random.uniform(*bmi_range)
    mass_kg = round(bmi * (height_m ** 2), 1)

    payload = {
        "input_data": {
            "input_unit_system": "metric",
            "subject": {
                "gender": gender,
                "age_category": "ADULT",
                "input_origin_region": target_region
            },
            "anchors": {
                "body_height": height_mm,
                "body_mass": mass_kg
            }
        },
        "output_settings": {
            "calculation": {
                "calculation_model": "AUTO",
                "target_region": target_region,
                "body_build_type": body_build_type
            },
            "requested_dimensions": {"bundle": "FULL_BODY"},
            "output_format": {
                "unit_system": "metric",
                "confidence_score_threshold": 0,
                "include_range_95": False,
                "include_iso_codes": False
            }
        }
    }
    return payload
```

<br>

## Response Handling Tips

- All API values are in mm — multiply by `0.001` before applying to Unity/Unreal transforms.
- `BONE` dimensions (structural, e.g. limb lengths, breadths) map to skeletal rig bone lengths. `FLESH` dimensions (circumferences, depths) drive blend shape weights and clothing simulation mesh targets. The `type` field in each dimension response indicates which category applies.
- For NPC crowd generation, vary `body_mass` around a population mean while keeping `body_height` fixed — this produces realistic body composition variation within a height cohort. Combine with `body_build_type: "OVERWEIGHT"` for heavier builds or `"ATHLETIC"` for leaner archetypes.
- `body_build_type: "ATHLETIC"` removes the NHANES civilian fat-distribution shift, producing leaner circumference proportions suitable for soldier, athlete, or action character archetypes.
- For runtime avatar generation (user creates avatar in-app), cache the full API response client-side — re-calling the API on every scene load adds unnecessary latency and wastes API quota.
- Normalise circumference values to [0, 1] using anatomically plausible min/max bounds before feeding into blend shape parameters — not the API's biological limit values, which represent clinical extremes rather than the visual body shape range useful for character design.
- `target_region` controls skeletal proportion calibration, not just scale. East Asian profiles (`ASIA_PACIFIC`) have proportionally different torso-to-leg ratios and shoulder widths compared to `EUROPE` — this affects rig believability for regional characters.

<br>
<br>
<br>

> ### **Disclaimer And Limitation Of Liability**
>
> All outputs of the DimensionsPot API ("Outputs") are statistically derived anthropometric predictions intended to support — not replace — professional judgment. They do not constitute medical, clinical, ergonomic, or professional advice, and must not be used as the sole basis for health decisions, product design, manufacturing tolerances, safety assessments, regulatory submissions, or contractual specifications. The Confidence Score is a proprietary heuristic index — not a statistical confidence interval.
>
> To the fullest extent permitted by applicable law, DimensionsPot and its operators disclaim all liability for any direct, indirect, incidental, consequential, or punitive damages — including bodily injury, property damage, financial loss, business interruption, or contractual liability — arising from reliance on Outputs.
>
> *This disclaimer does not exclude liability where prohibited by mandatory applicable law.*
