# Sports Equipment Rental — Automated Pre-Sizing

<br>

## Business Context

**The Problem:** The rental counter is where your revenue bottlenecks during peak hours. In practice, your staff isn't measuring every customer with a tape — they're pulling boots, helmets, and harnesses off the rack and watching the customer try them on until something fits. That trial-and-error loop burns 7–9 minutes per customer. The ceiling on your Saturday revenue is set not by demand but by how many fitting loops your counter can run in parallel.

**The Solution:** You already collect height and weight at online booking (or you can — it's one extra field). DimensionsPot takes those two numbers and returns a complete, 130-point anthropometric profile in under 10ms. Before the customer walks through the door, your system already knows their foot length, head circumference, chest, and inseam. Check-in becomes a two-minute handover, not a ten-minute trial session.

**The Procurement Edge:** Aggregate the same API calls across a season of bookings and you have a real size distribution for your actual customer base — not a catalog standard. Your procurement team orders 47 Medium boots and 23 Large helmets, not "a mixed pallet, roughly half-and-half." The mid-season emergency re-order cycle is the first line item most operators discover they can cut.

<br>

## Recommended API Configuration

| Parameter | Value | Reason |
|---|---|---|
| `anchors` | `body_height` + `body_mass` | PRIMARY_BOTH tier — available at booking; BONE ~85, FLESH ~78 confidence |
| `calculation_model` | `ADULT` | Rental customers are typically adults |
| `body_build_type` | `ATHLETIC` | Removes NHANES civilian fat-distribution shift; better fit for sports-active population |
| `bundle` | `FULL_BODY` | PPE and rental equipment sizing draws from multiple body regions |
| `confidence_score_threshold` | `70` | Retains all equipment-relevant FLESH dims (PRIMARY_BOTH FLESH ~78) while filtering genuinely uncertain outputs |
| `target_region` | Resort / rental location region | Calibrates to local population norms |

> **Threshold note:** With PRIMARY_BOTH anchors (height + weight), FLESH dimensions (circumferences such as chest, waist, calf) reach confidence ~78. Setting the threshold at 85 would suppress these dimensions entirely, blocking critical inputs like `chest_circumference` for wetsuit sizing and `calf_circumference` for ski boot shaft fit. Threshold 70 is the pragmatic minimum for rental applications.

### **Equipment mapping:**

| Equipment | Key Dimensions | Bundle |
|---|---|---|
| Ski boots | `foot_length`, `ankle_circumference`, `calf_circumference` | LEGS_FEET |
| Ski / cycling helmet | `head_circumference`, `head_breadth`, `head_length` | HEAD_FACE |
| Bicycle frame | `inseam_length`, `sitting_height`, `arm_length_total` | LEGS_FEET + TORSO + HAND_ARM |
| Wetsuit | `chest_circumference`, `waist_circumference_natural`, `hip_circumference`, `inseam_length` | TORSO + LEGS_FEET |
| Climbing harness | `waist_circumference_natural`, `hip_circumference`, `thigh_circumference` | TORSO + LEGS_FEET |
| Paddling / kayak PFD | `chest_circumference`, `shoulder_breadth` | TORSO |

<br>

## Sample Request

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
        "exact_age": 32.0,
        "age_category": "ADULT",
        "input_origin_region": "EUROPE"
      },
      "anchors": {
        "body_height": 1820.0,
        "body_mass": 88.0
      }
    },
    "output_settings": {
      "calculation": {
        "calculation_model": "ADULT",
        "target_region": "EUROPE",
        "body_build_type": "ATHLETIC"
      },
      "requested_dimensions": {
        "bundle": "FULL_BODY",
        "specific_dimensions": null
      },
      "output_format": {
        "unit_system": "metric",
        "confidence_score_threshold": 70,
        "include_range_95": true,
        "include_iso_codes": false
      }
    }
  }'
```

<br>

## Size Lookup Table Pattern

Pre-compute equipment size thresholds offline; the API call at booking time becomes a pure table lookup — no runtime ML inference required at the rental counter:

```python
# Offline lookup tables — adjust per manufacturer / brand specification
SKI_BOOT_SIZES = [
    (0,    235, "35"),
    (235,  245, "36"),
    (245,  255, "37"),
    (255,  265, "38"),
    (265,  275, "39"),
    (275,  285, "40"),
    (285,  295, "41"),
    (295,  305, "42"),
    (305,  315, "43"),
    (315,  325, "44"),
    (325,  335, "45"),
    (335, 9999, "46+"),
]

HELMET_SIZES = [
    (0,    520, "XS"),
    (520,  540, "S"),
    (540,  560, "M"),
    (560,  580, "L"),
    (580, 9999, "XL"),
]

def lookup_size(value_mm, table):
    for low, high, label in table:
        if low <= value_mm < high:
            return label
    return "Unknown"

def pre_size_rental(api_response):
    dims = api_response["body_dimensions"]

    foot    = dims["foot_length"]["value"]
    head    = dims["head_circumference"]["value"]

    # For safety-critical equipment, use the appropriate bound of range_95:
    #   · Ski boots — snug fit preferred → use point estimate (or lower bound)
    #   · Helmets and hard hats — safety margin → use UPPER bound (size up)
    foot_lower = dims["foot_length"]["range_95"][0]
    head_upper = dims["head_circumference"]["range_95"][1]

    return {
        "ski_boot":  lookup_size(foot_lower, SKI_BOOT_SIZES),    # snug fit
        "helmet":    lookup_size(head_upper, HELMET_SIZES),       # size up for safety
        "raw": {
            "foot_length_mm":       foot,
            "head_circumference_mm": head,
        }
    }
```

<br>

## Bicycle Frame Pre-Sizing

Bicycle frame size is derived primarily from inseam length (standing leg length). Use `inseam_length` from the LEGS_FEET bundle:

```python
BIKE_FRAME_SIZES = [
    # (inseam_min_mm, inseam_max_mm, frame_size_cm, label)
    (0,    710, 44, "XS"),
    (710,  740, 47, "S"),
    (740,  775, 50, "M"),
    (775,  810, 53, "M/L"),
    (810,  845, 56, "L"),
    (845,  880, 58, "L/XL"),
    (880, 9999, 61, "XL"),
]

def recommend_bike_frame(api_response):
    inseam = api_response["body_dimensions"]["inseam_length"]["value"]
    for lo, hi, frame_cm, label in BIKE_FRAME_SIZES:
        if lo <= inseam < hi:
            return {"size_label": label, "frame_cm": frame_cm, "inseam_mm": inseam}
    return {"size_label": "Custom fit required", "inseam_mm": inseam}
```

<br>

## Response Handling Tips

- For **ski boots and cycling shoes**, a snug fit is preferable — use the **point estimate** (or lower `range_95` bound) for size assignment.
- For **helmets, hard hats, and harnesses**, use the **upper `range_95` bound** — safety equipment should err on the side of one size larger when in doubt.
- Store the full API response in your booking record. If a customer reports poor fit on arrival, the stored body profile enables post-hoc analysis of systematic sizing errors across your inventory.
- Flag any dimension with `biological_limit_status: "OUT_OF_BOUNDS"` — these should be handled manually at check-in. Do not use out-of-bounds values for automated pre-sizing.
- P99 latency is 6–8 ms per call. Pre-sizing an entire day's bookings overnight in a nightly batch job is trivially fast even for a large resort.
- For children's rental, switch `age_category` to the appropriate pediatric value and omit `anchors` — the pediatric engine requires no measurements. See [COOKBOOK_06: Childrenswear & Children's Products](https://github.com/D-P0t/dimensionspot-docs/blob/main/integration-cookbooks/06_childrenswear_and_products.md).
- For **international resorts** (guests from multiple origins), always set `input_origin_region` per customer — body proportion norms differ significantly across regions, particularly for foot dimensions and head circumference.

<br>
<br> 

> ### **Disclaimer And Limitation Of Liability**
>
> All outputs of the DimensionsPot API ("Outputs") are statistically derived anthropometric predictions intended to support — not replace — professional judgment. They do not constitute medical, clinical, ergonomic, or professional advice, and must not be used as the sole basis for health decisions, product design, manufacturing tolerances, safety assessments, regulatory submissions, or contractual specifications. The Confidence Score is a proprietary heuristic index — not a statistical confidence interval.
>
> To the fullest extent permitted by applicable law, DimensionsPot and its operators disclaim all liability for any direct, indirect, incidental, consequential, or punitive damages — including bodily injury, property damage, financial loss, business interruption, or contractual liability — arising from reliance on Outputs.
>
> *This disclaimer does not exclude liability where prohibited by mandatory applicable law.*
