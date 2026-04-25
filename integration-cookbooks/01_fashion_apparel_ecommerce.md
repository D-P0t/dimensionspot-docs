# Fashion & Apparel E-commerce — Size Recommendation Engine

<br>

## Business Context

**The Problem:** Customers don’t know their body measurements. And they refuse to measure themselves. When you ask for their chest or waist size, they guess. When they guess, they bracket-buy—sticking you with the reverse logistics bill and killing your margins through shipping, restocking, and deadstock. Or worse: they abandon the cart entirely.

**The Solution:** The fix isn't a better size chart. It's a better input. The only two numbers every customer actually knows are height and weight. DimensionsPot takes those two inputs and generates a complete, 130-point anthropometric profile in under 10ms. You get the chest, natural waist, hips, and inseam measurements required to confidently recommend a single size at checkout.

**The Global Edge:** Selling cross-border? A "Size M" in Tokyo has different skeletal proportions than a "Size M" in Berlin. DimensionsPot handles the demographic math natively. By defining the `input_origin_region` (your customer) and `target_region` (your brand's fit model), the API instantly translates body ratios between populations in a single request.

<br>

## Recommended API Configuration

| Parameter | Value | Reason |
|---|---|---|
| `anchors` | `body_height` + `body_mass` | PRIMARY_BOTH tier — BONE dims ~85, FLESH dims ~78 confidence |
| `calculation_model` | `AUTO` | Routes to ADULT for ages 18+; safe default |
| `body_build_type` | `CIVILIAN` | NHANES general-population body composition morphing |
| `bundle` | `TORSO` | Returns 29 torso dimensions — all clothing-relevant girths and lengths |
| `input_origin_region` | Customer's region | Normalises input anchors to ANSUR global baseline before inference |
| `target_region` | Brand's sizing-chart origin region | Calibrates output proportions to the population your size chart was built for |
| `confidence_score_threshold` | `75` | Passes all FLESH dims at PRIMARY_BOTH (~78) while filtering genuinely low-confidence outputs |

> **Threshold note:** PRIMARY_BOTH BONE dimensions score ~85; FLESH dimensions ~78. Setting `confidence_score_threshold: 80` would suppress most circumference dimensions (FLESH) — exactly the ones needed for apparel sizing. Threshold 75 retains everything clothing-relevant.

**Tip — Cross-regional sizing:** Set `input_origin_region` to the customer's location and `target_region` to the region your size chart was built for. The Universal Translator eliminates the Double Penalty Paradox that affects naive regional scaling.

*Example:* Asian customer, European brand → `input_origin_region: "ASIA_PACIFIC"`, `target_region: "EUROPE"`.

**Tip — Plus-size / curve lines:** Set `body_build_type: "OVERWEIGHT"` for shoppers with BMI > 30 to activate BMI-stratified NHANES morphing. Circumference dimensions adjust accordingly.

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
        "gender": "female",
        "exact_age": 28.0,
        "age_category": "ADULT",
        "input_origin_region": "EUROPE"
      },
      "anchors": {
        "body_height": 1680.0,
        "body_mass": 65.0
      }
    },
    "output_settings": {
      "calculation": {
        "calculation_model": "AUTO",
        "target_region": "EUROPE",
        "body_build_type": "CIVILIAN"
      },
      "requested_dimensions": {
        "bundle": "TORSO",
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

## Key Dimensions for Apparel Sizing

| API Key | Label | Type | Bundle | Use |
|---|---|---|---|---|
| `chest_circumference` | Chest Circumference | FLESH | TORSO | Tops, jackets, shirts |
| `waist_circumference_natural` | Waist Circumference (Natural) | FLESH | TORSO | Trousers, skirts, dresses — clothing standard (ISO 6.4.11) |
| `hip_circumference` | Hip Circumference | FLESH | TORSO | Trousers, skirts, dresses |
| `shoulder_breadth` | Shoulder Breadth | BONE | TORSO | Jackets, shirts, coats |
| `back_waist_length` | Back Waist Length | BONE | TORSO | Dress and jacket back length |
| `bust_circumference` | Bust Circumference | FLESH | TORSO | Fitted tops, bras |
| `underbust_circumference` | Underbust Circumference | FLESH | TORSO | Bra band size (EN 13402) |
| `sitting_height` | Sitting Height | BONE | TORSO | Dress length calibration |
| `inseam_length` | Inseam Length | BONE | LEGS_FEET | Trouser leg length |
| `thigh_circumference` | Thigh Circumference | FLESH | LEGS_FEET | Trouser thigh fit |
| `calf_circumference` | Calf Circumference | FLESH | LEGS_FEET | Boot shaft, hosiery |

> `inseam_length`, `thigh_circumference`, and `calf_circumference` are in the `LEGS_FEET` bundle. To retrieve them alongside torso dimensions in a single call, use `bundle: "FULL_BODY"` or list all needed keys explicitly in `specific_dimensions`.

> `bust_circumference` and `underbust_circumference` are predicted for **all genders**. For menswear, they provide an additional chest-fit signal alongside `chest_circumference`.

> **Waist note:** `waist_circumference_natural` (ISO 6.4.11, narrowest torso point) is the apparel standard. `waist_circumference_omphalion` (navel level) is the clinical/epidemiological standard (NHANES/WHO). Use `waist_circumference_natural` for clothing size charts.

<br>

## Size Chart Mapping — Pattern

Map API dimensions against your stored size chart thresholds client-side. No runtime ML required:

```python
# Example: map torso dimensions to garment sizes
# Adjust thresholds per brand/product category

SIZE_CHART_FEMALE = {
    # (chest_min, chest_max, waist_min, waist_max, hip_min, hip_max) → size label
    "XS": (770, 830,  580, 630,  840, 890),
    "S":  (830, 890,  630, 680,  890, 940),
    "M":  (890, 950,  680, 730,  940, 990),
    "L":  (950, 1010, 730, 800,  990, 1050),
    "XL": (1010, 1100, 800, 880, 1050, 1130),
}

def recommend_size(chest_mm, waist_mm, hip_mm, size_chart):
    """
    Returns best-fit size and a between-sizes flag.
    chest/waist/hip in mm (API metric output).
    """
    candidates = []
    for label, (ch_lo, ch_hi, w_lo, w_hi, h_lo, h_hi) in size_chart.items():
        if ch_lo <= chest_mm < ch_hi and w_lo <= waist_mm < w_hi and h_lo <= hip_mm < h_hi:
            candidates.append(label)
    if len(candidates) == 1:
        return candidates[0], False
    elif len(candidates) > 1:
        return candidates[0], True   # between-sizes — flag for UI
    return None, True                # no match — flag for manual selection

dims = response["body_dimensions"]
size, between = recommend_size(
    dims["chest_circumference"]["value"],
    dims["waist_circumference_natural"]["value"],
    dims["hip_circumference"]["value"],
    SIZE_CHART_FEMALE,
)
```

<br>

## Handling Size Boundary Cases with `range_95`

When a customer's predicted dimension lands near a size boundary, use the 95% prediction interval to surface the uncertainty:

```python
def size_with_range_check(dim_key, size_chart_col, response, size_chart):
    """
    Returns recommended size and a flag if the range_95 spans two sizes.
    """
    dim = response["body_dimensions"][dim_key]
    value     = dim["value"]
    lower_95  = dim["range_95"][0]
    upper_95  = dim["range_95"][1]

    size_point = recommend_size_single(value, size_chart_col, size_chart)
    size_lower = recommend_size_single(lower_95, size_chart_col, size_chart)
    size_upper = recommend_size_single(upper_95, size_chart_col, size_chart)

    between_sizes = (size_lower != size_upper)
    return size_point, between_sizes
```

UI recommendation: when `between_sizes = True`, show "We recommend size M — if you prefer a relaxed fit, also consider L."

<br>

## Response Handling Tips

- Map `chest_circumference`, `waist_circumference_natural`, and `hip_circumference` against your size chart thresholds. For dresses and one-piece garments, the governing dimension is typically `hip_circumference`.
- Use `range_95` for boundary handling: if the 95% interval spans two size thresholds, present both options and let the customer choose based on their preferred fit (snug vs. relaxed).
- Check `biological_limit_status` before mapping: dimensions flagged `"OUT_OF_BOUNDS"` fall outside population normal range and should not drive automated size recommendations — prompt the customer to contact support or visit a store.
- `type: "MEASURED"` dimensions (the anchors the caller supplied) carry `confidence_score: 100` and are returned as-is — the engine never overwrites them.
- For trouser recommendations in a single API call, use `bundle: "FULL_BODY"` or add `"inseam_length"`, `"thigh_circumference"` to `specific_dimensions`.
- When `exact_age` is not collected, omit the field entirely — the engine defaults to ADULT. Providing `exact_age` improves the Deurenberg body-composition correction used internally, so collect it if your flow permits.
<br>
<br> 
<br>
<br>

> <br>
>
> ### **Disclaimer And Limitation Of Liability**
>
> All outputs of the DimensionsPot API ("Outputs") are statistically derived anthropometric predictions intended to support — not replace — professional judgment. They do not constitute medical, clinical, ergonomic, or professional advice, and must not be used as the sole basis for health decisions, product design, manufacturing tolerances, safety assessments, regulatory submissions, or contractual specifications. The Confidence Score is a proprietary heuristic index — not a statistical confidence interval.
>
> To the fullest extent permitted by applicable law, DimensionsPot and its operators disclaim all liability for any direct, indirect, incidental, consequential, or punitive damages — including bodily injury, property damage, financial loss, business interruption, or contractual liability — arising from reliance on Outputs.
>
> *This disclaimer does not exclude liability where prohibited by mandatory applicable law.*
>
> <br> 