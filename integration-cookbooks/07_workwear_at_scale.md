# Workwear at Scale — Workforce Sizing from HR Data

<br>

## Business Context

**The Problem:** A uniform rollout isn't a design problem — it's a data collection problem with a predictable failure pattern. Sizing forms go out, half don't come back, the ones that do contain guesses, and procurement places an order based on a mix of assumptions and buffer stock. Two months later you're re-ordering Mediums while a pallet of XLs sits in the warehouse. Physical sizing sessions work better and cost you weeks per site.

**The Solution:** Your HRIS already stores height and weight (safety records, medical surveillance, site access). DimensionsPot converts those two fields into a complete, 130-point anthropometric profile in under 10ms. You get the exact chest, waist, inseam, and foot length measurements required to define your order specifications before the first employee walks through the door. You cut the planning cycle from weeks to seconds — a workforce of 1,000 runs in under 10 seconds at moderate concurrency.

**The Procurement Edge:** Turn HR data into a precise demand forecast. By processing your workforce list through the API, logistics knows exactly how many units of each size to stock for the specific group being outfitted. You secure bulk discounts with confidence, accelerate the entire purchasing cycle, and eliminate the emergency re-order cycle that eats your margin every rollout.

<br>

## Recommended API Configuration

| Parameter | Value | Reason |
|---|---|---|
| `anchors` | `body_height` + `body_mass` | Standard HR data fields; PRIMARY_BOTH tier |
| `body_build_type` | `ATHLETIC` | Physical and manual labour workforces trend toward higher lean mass than the general NHANES civilian population; removes the civilian fat-distribution shift |
| `bundle` | `FULL_BODY` | Workwear sizing draws from torso, arms, legs, hands, and feet simultaneously |
| `confidence_score_threshold` | `75` | Retains all workwear-relevant FLESH dimensions (PRIMARY_BOTH FLESH ~78) while filtering genuinely uncertain outputs |
| `target_region` | Workforce deployment region | Accounts for regional body proportion differences — critical for multinational workforces |

> For predominantly desk-based or office workforces receiving uniform shirts or light workwear, use `body_build_type: "CIVILIAN"` instead. `ATHLETIC` applies the NHANES lean-mass adjustment; `CIVILIAN` uses the general population baseline.

<br>

### Garment category → dimension mapping:

| Garment | Key Dimensions | Bundle |
|---|---|---|
| Work jacket / shirt | `chest_circumference`, `shoulder_breadth`, `arm_length_total`, `neck_circumference` | TORSO + HAND_ARM |
| Coverall / work suit | `chest_circumference`, `waist_circumference_natural`, `hip_circumference`, `inseam_length`, `back_waist_length`, `arm_length_total` | FULL_BODY |
| Work trousers | `waist_circumference_natural`, `hip_circumference`, `inseam_length`, `thigh_circumference` | TORSO + LEGS_FEET |
| Work gloves | `hand_length`, `hand_breadth`, `hand_circumference` | HAND_ARM |
| Work boots / shoes | `foot_length`, `foot_breadth`, `ankle_circumference` | LEGS_FEET |
| Cap / headwear | `head_circumference`, `head_breadth` | HEAD_FACE |
| High-visibility vest / jacket | `chest_circumference`, `shoulder_breadth`, `back_waist_length` | TORSO |

<br>

## Sample Request

```bash
curl -X POST "https://dimensionspot-bodysize-engine.p.rapidapi.com/v1/predict" \
  -H "Content-Type: application/json" \
  -H "X-RapidAPI-Key: YOUR_KEY" \
  -H "X-RapidAPI-Host: dimensionspot-bodysize-engine.p.rapidapi.com" \
  -d '{
    "input_data": {
      "input_unit_system": "metric",
      "subject": {
        "gender": "male",
        "exact_age": 41.0,
        "age_category": "ADULT",
        "input_origin_region": "EUROPE"
      },
      "anchors": {
        "body_height": 1790.0,
        "body_mass": 95.0
      }
    },
    "output_settings": {
      "calculation": {
        "calculation_model": "AUTO",
        "target_region": "EUROPE",
        "body_build_type": "ATHLETIC"
      },
      "requested_dimensions": {
        "bundle": "FULL_BODY",
        "specific_dimensions": null
      },
      "output_format": {
        "unit_system": "metric",
        "confidence_score_threshold": 75,
        "include_range_95": true,
        "include_iso_codes": false
      }
    }
  }'
```

<br>

## Batch Processing Pattern

Size an entire workforce from an HR export in a single script:

```python
import requests

API_URL = "https://dimensionspot-bodysize-engine.p.rapidapi.com/v1/predict"
HEADERS = {
    "Content-Type": "application/json",
    "X-RapidAPI-Key": "YOUR_KEY",
    "X-RapidAPI-Host": "dimensionspot-bodysize-engine.p.rapidapi.com"
}

def size_employee(employee_id, gender, age, height_mm, weight_kg, region="GLOBAL"):
    payload = {
        "input_data": {
            "input_unit_system": "metric",
            "subject": {
                "gender": gender,
                "exact_age": float(age),
                "age_category": "ADULT",
                "input_origin_region": region
            },
            "anchors": {
                "body_height": float(height_mm),
                "body_mass": float(weight_kg)
            }
        },
        "output_settings": {
            "calculation": {
                "calculation_model": "AUTO",
                "target_region": region,
                "body_build_type": "ATHLETIC"
            },
            "requested_dimensions": {"bundle": "FULL_BODY"},
            "output_format": {
                "unit_system": "metric",
                "confidence_score_threshold": 75,
                "include_range_95": True,
                "include_iso_codes": False
            }
        }
    }
    response = requests.post(API_URL, headers=HEADERS, json=payload, timeout=10)
    response.raise_for_status()
    return employee_id, response.json()


# Example: size a list of employees from HR export
employees = [
    {"id": "EMP001", "gender": "male",   "age": 34, "height_mm": 1780, "weight_kg": 88,  "region": "EUROPE"},
    {"id": "EMP002", "gender": "female", "age": 29, "height_mm": 1650, "weight_kg": 62,  "region": "ASIA_PACIFIC"},
    {"id": "EMP003", "gender": "male",   "age": 47, "height_mm": 1720, "weight_kg": 105, "region": "LATAM"},
]

results = {}
for emp in employees:
    emp_id, profile = size_employee(
        emp["id"], emp["gender"], emp["age"],
        emp["height_mm"], emp["weight_kg"], emp["region"]
    )
    results[emp_id] = profile
    print(f"{emp_id}: {len(profile['body_dimensions'])} dimensions computed")
```

<br>

## Inventory Planning Pattern

Aggregate predicted size distributions across a planned workforce to model stock requirements before procurement:

```python
from collections import Counter

COVERALL_SIZES = [
    (0,    880, "XS"),
    (880,  960, "S"),
    (960,  1040, "M"),
    (1040, 1120, "L"),
    (1120, 1200, "XL"),
    (1200, 9999, "XXL"),
]

def lookup_coverall_size(chest_mm):
    for lo, hi, label in COVERALL_SIZES:
        if lo <= chest_mm < hi:
            return label
    return "Unknown"

# Aggregate coverall size distribution across workforce
coverall_counter = Counter()
for emp_id, profile in results.items():
    dims = profile["body_dimensions"]
    if "chest_circumference" in dims:
        chest = dims["chest_circumference"]["value"]
        coverall_counter[lookup_coverall_size(chest)] += 1

print("Coverall size distribution:")
for size_label, count in sorted(coverall_counter.items()):
    print(f"  {size_label}: {count}")

# Extend the same pattern for any garment type:
# trousers  → waist_circumference_natural + inseam_length (dual lookup)
# gloves    → hand_circumference
# boots     → foot_length
# headwear  → head_circumference
```

> The same aggregation pattern applies to any garment type — replace `chest_circumference` with the governing dimension for that category (see the garment mapping table above) and substitute your supplier's size thresholds.

<br>

## Response Handling Tips

- Flag any employee with a dimension marked `biological_limit_status: "OUT_OF_BOUNDS"` for manual measurement — do not use out-of-bounds values for automated garment assignment.
- For multinational workforces, always set `input_origin_region` per employee. Regional body proportion differences are significant for shoulder-to-hip ratios, torso length, and arm length — applying a single regional default to a mixed workforce produces systematic sizing errors.
- Store `input_origin_region` and `target_region` alongside each employee's dimensional profile. A `chest_circumference` calibrated for `EUROPE` is a different number than the same employee's `chest_circumference` calibrated for `ASIA_PACIFIC`. The stored region is required context for any future re-use of the profile.
- `body_build_type: "ATHLETIC"` applies the NHANES lean-mass adjustment and is the appropriate baseline for physical and manual labour roles. Switch to `"CIVILIAN"` for office or desk-based workforces.
- The `AFRICA` region uses male-centric calibration data with a −10% confidence penalty on FLESH dimensions for female employees. Treat FLESH dimension outputs as indicative for this subgroup and prioritise on-site confirmation where possible.
- P99 latency is 6–8 ms per call. A workforce of 1,000 employees can be fully profiled in under 10 seconds at moderate API concurrency. For large batches, process requests concurrently rather than sequentially to stay within this window.

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
