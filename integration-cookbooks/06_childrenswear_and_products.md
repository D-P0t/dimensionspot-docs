# Childrenswear & Children's Products

<br>

## Business Context

**The Problem:** "Ages 2–4" isn't a size — it's a population estimate disguised as a label. Designers can't validate their patterns against a known dimensional envelope, parents can't trust the tags, and retailers sourcing globally have no reliable way to verify whether an "Ages 2–4" from one region covers the same children as the same label from another.

**The Solution:** DimensionsPot converts age and gender into a complete, 130-point anthropometric profile in under 10ms. Grounded in CDC-validated population data, the API returns median dimensions for height, weight, chest, waist, and 126 other metrics — plus a 95% prediction interval on every one. You stop relying on vague age brackets and start working with population-calibrated specifications you can verify.

- ***The Designer's Edge:*** Query the API at the boundaries and midpoint of an age bracket to establish the exact dimensional envelope your pattern needs to cover. Your size chart becomes a reflection of the actual target population, not a competitor's guesswork copied forward one more season.

- ***The Parent's Edge:*** Decode labels for your customers. Show exactly what "Ages 2–4" means in centimeters, as a range — chest, height, inseam. Parents with a measured child can compare directly, which eliminates the most common reason for returns in the category.

- ***The Retailer's Edge:*** Validate cross-border fit before the PO goes out. The dimensional envelope behind the same age label varies significantly between an Asian supplier and a European manufacturer. By comparing profiles across `target_region` settings, buyers identify proportional mismatches before the container ships, not after it lands.

**The Longevity Projection:** Power your own growth forecasting. By comparing current age data against a 12 or 18-month projection against CDC median growth curves, your application can estimate when a typical child will outgrow a product. "Fits most children until approximately age 3.5" — a data point that builds parent trust in a category where every competitor is still hiding behind vague brackets.

<br>

> **Key difference from the adult engine:** `body_height` and `body_mass` are **outputs** in pediatric mode, not inputs.

<br>

## Recommended API Configuration

| Parameter | Value | Reason |
|---|---|---|
| `age_category` | Appropriate pediatric value | Triggers automatic routing to LMS/CDC engine |
| `exact_age` | Float years (preferred) | More precise LMS interpolation between CDC table entries |
| `anchors` | `{}` (empty) or omit | Not required for PEDIATRIC — engine uses age + gender |
| `calculation_model` | `PEDIATRIC` | Explicit; also auto-activated by any pediatric `age_category` or `exact_age ≤ 20.0` |
| `bundle` | `TORSO` for clothing; `FULL_BODY` for products | FULL_BODY needed when head, leg, and torso dimensions are all required |
| `confidence_score_threshold` | `0` | LMS dims are confidence 99; Ridge hybrid dims capped at 80 — set to 0 and filter client-side |

### Age category mapping:

| `age_category` | Typical age range | `exact_age` examples |
|---|---|---|
| `INFANT` | ~0–18 months | `0.5`, `1.0`, `1.5` |
| `TODDLER` | ~18 months–3.5 years | `2.0`, `2.5`, `3.0` |
| `CHILD` | ~3–10 years | `4.0`, `6.5`, `9.0` |
| `PRE_TEEN` | ~10–13 years | `10.5`, `12.0` |
| `TEEN` | ~13–20 years | `14.0`, `16.5`, `19.0` |

> Always pass `exact_age` as a float (e.g., `7.5` for 7 years 6 months). When only `age_category` is provided, the engine uses the bracket's median age and adds a warning to `header.meta_warnings` — the median can be several years from the child's actual age.

### Edge cases:
- `exact_age: 0.0` is clamped to 0.5 months (minimum CDC table age) with a warning in `header.meta_warnings`.
- Ages above 20.0 years are clamped to 240 months with a warning. For adults, use the ADULT engine.
- Any internal LMS calculation error returns a graceful empty `{}` `body_dimensions` response. Always check for an empty response in your handler.

<br>

## Sample Requests

### Designer's Edge — Age Bracket Boundary Profile

To define the dimensional envelope for a product labeled "Ages 2–4", call the API at the lower and upper bracket boundaries (`exact_age: 2.0` and `exact_age: 4.0`). The difference between the two responses sets the dimensional range the product must accommodate.

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
        "exact_age": 4.0,
        "age_category": "CHILD",
        "input_origin_region": "EUROPE"
      },
      "anchors": {}
    },
    "output_settings": {
      "calculation": {
        "calculation_model": "PEDIATRIC",
        "target_region": "EUROPE",
        "body_build_type": "CIVILIAN"
      },
      "requested_dimensions": {
        "bundle": "FULL_BODY",
        "specific_dimensions": null
      },
      "output_format": {
        "unit_system": "metric",
        "confidence_score_threshold": 0,
        "include_range_95": true,
        "include_iso_codes": false
      }
    }
  }'
```

> Use `bundle: "TORSO"` for clothing-only use cases to reduce payload size. Use `bundle: "FULL_BODY"` when head, leg, and torso dimensions are all needed — for car seats, bikes, or complete product fit assessments.

<br>

### Retailer's Edge — Cross-Regional Comparison

Call the same age twice with different `target_region` values to compare the CDC-calibrated dimensional profiles for two populations. The delta between responses shows whether a product sized for one market will fit another.

```bash
# Call 1 — European profile for age 4 male
curl -X POST "https://dimensionspot-bodysize-engine.p.rapidapi.com/v1/predict" \
  -H "Content-Type: application/json" \
  -H "X-RapidAPI-Key: YOUR_KEY" \
  -H "X-RapidAPI-Host: dimensionspot-bodysize-engine.p.rapidapi.com" \
  -d '{
    "input_data": {
      "input_unit_system": "metric",
      "subject": {
        "gender": "male",
        "exact_age": 4.0,
        "age_category": "CHILD",
        "input_origin_region": "EUROPE"
      },
      "anchors": {}
    },
    "output_settings": {
      "calculation": {
        "calculation_model": "PEDIATRIC",
        "target_region": "EUROPE",
        "body_build_type": "CIVILIAN"
      },
      "requested_dimensions": { "bundle": "FULL_BODY" },
      "output_format": {
        "unit_system": "metric",
        "confidence_score_threshold": 0,
        "include_range_95": false,
        "include_iso_codes": false
      }
    }
  }'

# Call 2 — identical request, target_region changed to ASIA_PACIFIC
# Replace "target_region": "EUROPE" with "target_region": "ASIA_PACIFIC"
# and "input_origin_region": "EUROPE" with "input_origin_region": "ASIA_PACIFIC"
```

> Compare the two responses dimension by dimension. A positive delta (ASIA_PACIFIC − EUROPE) means the Asian population profile is larger for that dimension at this age; negative means smaller. If deltas on governing dimensions (e.g., `chest_circumference`, `body_height`) exceed your product's fit tolerance, the size range needs adjustment for the target market.

<br>

## Key Dimensions by Product Category

### Childrenswear:

| API Key | Label | Use |
|---|---|---|
| `body_height` | Body Height (predicted) | Garment total-length sizing; size chart lookup |
| `chest_circumference` | Chest Circumference | Top / jacket / dress sizing |
| `waist_circumference_natural` | Waist Circumference | Trouser / skirt / shorts sizing |
| `hip_circumference` | Hip Circumference | Trouser / skirt sizing (PRE_TEEN, TEEN) |
| `inseam_length` | Inseam Length | Trouser leg length |
| `sitting_height` | Sitting Height | Dress / top body length calibration |
| `shoulder_breadth` | Shoulder Breadth | Jacket / coat shoulder width |

### Car seats & harness products:

| API Key | Label | Use |
|---|---|---|
| `body_height` | Body Height | Height limit check against seat spec |
| `body_mass` | Body Mass | Weight limit check against seat spec |
| `sitting_height` | Sitting Height | Head clearance above seat back |
| `shoulder_breadth` | Shoulder Breadth | Shoulder harness slot positioning |
| `hip_circumference` | Hip Circumference | Bucket shell width fit |

### Strollers & pushchairs:

| API Key | Label | Use |
|---|---|---|
| `body_height` | Body Height | Lie-flat length for infant mode; overall fit |
| `body_mass` | Body Mass | Weight limit |
| `sitting_height` | Sitting Height | Seat back height requirement |
| `shoulder_breadth` | Shoulder Breadth | Harness width |

### Baby carriers:

| API Key | Label | Use |
|---|---|---|
| `body_mass` | Body Mass | Carrier weight range eligibility |
| `body_height` | Body Height | Carrier height range eligibility |
| `sitting_height` | Sitting Height | Panel height for back support |

### Bikes & ride-on toys:

| API Key | Label | Use |
|---|---|---|
| `inseam_length` | Inseam Length | Wheel size / frame size selection |
| `body_height` | Body Height | Overall bike size guide |
| `body_mass` | Body Mass | Weight limit for ride-on toys |

### Helmets (bike, ski, skate):

| API Key | Label | Use |
|---|---|---|
| `head_circumference` | Head Circumference | Helmet size selection |

<br>

> **Head circumference note:** Direct LMS/CDC data is available up to 36 months. For children older than 3, the engine uses Ridge hybrid (confidence capped at 80) and clamps to the 36-month LMS value as an anchor. Always use the `range_95` upper bound for helmet sizing and check `header.meta_warnings` for clamping notices.

<br>

## Confidence Scores in Pediatric Mode

| Dimension Source | Dimensions | Confidence Score |
|---|---|---|
| **LMS / CDC** (direct table interpolation) | `body_height`, `body_mass`, `head_circumference` (ages 0–36 months) | **99** — exact tabular interpolation |
| **Ridge hybrid** (adult Ridge scaled to LMS-derived BH + BM) | All remaining ~127 dimensions | **Capped at 80** |

> `body_build_type` has **no effect** on pediatric responses — the LMS engine does not apply NHANES civilian morphing. The parameter is accepted without error but ignored.

<br>

## Age Bracket Envelope Pattern

Query the API at the boundaries and midpoint of an age bracket to build a complete dimensional specification for a product's target age range:

```python
def _build_request(exact_age, gender, region, bundle):
    return {
        "input_data": {
            "input_unit_system": "metric",
            "subject": {
                "gender": gender,
                "exact_age": round(exact_age, 2),
                "age_category": _classify_age(exact_age),
                "input_origin_region": region
            },
            "anchors": {}
        },
        "output_settings": {
            "calculation": {
                "calculation_model": "PEDIATRIC",
                "target_region": region,
                "body_build_type": "CIVILIAN"
            },
            "requested_dimensions": {"bundle": bundle},
            "output_format": {
                "unit_system": "metric",
                "confidence_score_threshold": 0,
                "include_range_95": True,
                "include_iso_codes": False
            }
        }
    }

def age_bracket_envelope(age_start, age_end, gender, region="EUROPE", bundle="TORSO"):
    """
    Build requests for the lower boundary, midpoint, and upper boundary of an age bracket.
    Call each payload against the API. The resulting three profiles define the dimensional
    envelope a product labeled "Ages X–Y" must accommodate.
    """
    mid_age = (age_start + age_end) / 2.0
    return {
        "lower": _build_request(age_start, gender, region, bundle),
        "mid":   _build_request(mid_age,   gender, region, bundle),
        "upper": _build_request(age_end,   gender, region, bundle),
    }

def _classify_age(age_years):
    if age_years < 1.5:   return "INFANT"
    elif age_years < 3.5: return "TODDLER"
    elif age_years < 10:  return "CHILD"
    elif age_years < 13:  return "PRE_TEEN"
    else:                 return "TEEN"


# Usage — define dimensional envelope for a product labeled "Ages 2–4", European market
payloads = age_bracket_envelope(2.0, 4.0, "male", region="EUROPE", bundle="TORSO")
# Call API for payloads["lower"], payloads["mid"], payloads["upper"]
# → chest_circumference at 2.0 / 3.0 / 4.0 defines the product's required chest range
# → inseam_length at the same ages defines the trouser length range
```

> For consumer-facing applications (Parent's Edge): derive `exact_age` from the child's date of birth using `(target_date - date_of_birth).days / 365.25` before calling `_build_request`. The API itself takes age in years, not a date.

<br>

## Longevity Projection Pattern

Estimate the age at which a typical child will outgrow a product's dimensional limits. All projections are based on CDC 50th percentile growth curves — the population median. Larger children will reach limits sooner; smaller children later.

```python
def longevity_projection(starting_age, gender, product_limits, region="EUROPE"):
    """
    Iterate monthly from starting_age until a CDC median dimension exceeds a product limit.

    starting_age:   float — child's age in years at the start of product use
    product_limits: dict of {dimension_key: max_value}
                    e.g. {"body_height": 1050, "body_mass": 18.0}
    Returns (within_limits_at_start: bool, outgrown_at_age: float | None)
    """
    for step in range(49):   # 0 to 48 months ahead
        check_age = starting_age + (step / 12.0)
        payload = _build_request(check_age, gender, region, "FULL_BODY")
        # → call API with payload
        # dims = response["body_dimensions"]
        # for dim_key, max_val in product_limits.items():
        #     if dims[dim_key]["value"] > max_val:
        #         within_limits_at_start = (step > 0)
        #         return within_limits_at_start, round(check_age, 2)

    return True, None   # within limits beyond 4-year projection horizon


# Usage — car seat: height limit 105 cm (1050 mm), weight limit 18 kg
# Child begins using the seat at age 1.0
PRODUCT_LIMITS = {
    "body_height": 1050,   # mm
    "body_mass":   18.0,   # kg
}

fits, outgrown_at = longevity_projection(
    starting_age=1.0,
    gender="male",
    product_limits=PRODUCT_LIMITS,
    region="EUROPE",
)
# outgrown_at is the CDC median age at which the first limit is exceeded.
# Display as: "Based on CDC growth data, most children outgrow this seat
#              by approximately age {outgrown_at:.1f}."
```

> Use `range_95` upper bound values instead of `value` when projecting for safety-critical products (car seats, harnesses, cribs) — this ensures the recommendation accounts for larger children in the population, not only the median.

<br>

## Response Handling Tips

- `body_height` and `body_mass` are predicted **outputs** — they represent CDC 50th percentile values for the given age and gender, not inputs. They cannot be overridden by passing values in `anchors`.
- `range_95` reflects population spread at the given age, not model uncertainty. The interval width represents the difference between approximately the 5th and 95th percentile child for that dimension. **For product design (Designer's Edge):** the median `value` is the reference point for your size chart midpoint; the `range_95` bounds define coverage for the population extremes. **For safety-critical products (car seats, cribs, harnesses):** always use the `range_95` upper bound in longevity projections — larger children reach dimensional limits sooner.
- **For label decoding (Parent's Edge):** query at `exact_age: 2.0` and `exact_age: 4.0` and surface the `value` of each governing dimension (e.g., chest, height, inseam) as the dimensional range implied by the "Ages 2–4" label. Parents can compare their child's measured values directly against this range.
- **For cross-regional comparisons (Retailer's Edge):** store `target_region` alongside each API response. A `chest_circumference` value calibrated for `EUROPE` is a different number than the same child's `chest_circumference` calibrated for `ASIA_PACIFIC`. Always label stored profiles with their region.
- For childrenswear season planning, query at `exact_age + 0.5` (6 months ahead of expected delivery or season start) to size for the period the garment will actually be worn, not the date of purchase.
- Always check `header.meta_warnings` for clamping notices (`exact_age: 0.0` clamped to 0.5 months; `head_circumference` clamped at 36 months for children older than 3) before using affected dimensions in product specifications.
- For bike sizing, `inseam_length` is the governing dimension — the same lookup table pattern used in the Sports Equipment Rental cookbook applies directly.

<br>
<br> 

> ### **Disclaimer And Limitation Of Liability**
>
> All outputs of the DimensionsPot API ("Outputs") are statistically derived anthropometric predictions intended to support — not replace — professional judgment. They do not constitute medical, clinical, ergonomic, or professional advice, and must not be used as the sole basis for health decisions, product design, manufacturing tolerances, safety assessments, regulatory submissions, or contractual specifications. The Confidence Score is a proprietary heuristic index — not a statistical confidence interval.
>
> To the fullest extent permitted by applicable law, DimensionsPot and its operators disclaim all liability for any direct, indirect, incidental, consequential, or punitive damages — including bodily injury, property damage, financial loss, business interruption, or contractual liability — arising from reliance on Outputs.
>
> *This disclaimer does not exclude liability where prohibited by mandatory applicable law.*
