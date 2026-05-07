# DimensionsPot API — Agent Instructions

This document helps AI coding agents (Claude Code, GitHub Copilot, Cursor) understand
how to correctly integrate DimensionsPot API.

## Endpoint

POST https://dimensionspot-bodysize-engine.p.rapidapi.com/v1/predict

## Required headers

```
X-RapidAPI-Key: {user's RapidAPI key}
X-RapidAPI-Host: dimensionspot-bodysize-engine.p.rapidapi.com
Content-Type: application/json
```

## Minimum viable payload (adult)

```json
{
  "input_data": {
    "subject": {
      "gender": "male"
    },
    "anchors": {
      "body_height": 1780
    }
  }
}
```

Returns all 130 FULL_BODY dimensions in metric with 95% intervals and ISO codes.

## Full payload with all common fields

```json
{
  "input_data": {
    "input_unit_system": "metric",
    "subject": {
      "gender": "male",
      "exact_age": 35.0,
      "age_category": "ADULT",
      "input_origin_region": "EUROPE"
    },
    "anchors": {
      "body_height": 1780,
      "body_mass": 82.0
    }
  },
  "output_settings": {
    "calculation": {
      "calculation_model": "AUTO",
      "target_region": "EUROPE",
      "body_build_type": "CIVILIAN"
    },
    "requested_dimensions": {
      "bundle": "FULL_BODY"
    },
    "output_format": {
      "unit_system": "metric",
      "confidence_score_threshold": 0,
      "include_range_95": true,
      "include_iso_codes": true
    }
  }
}
```

## Units — most common mistake

`body_height` is in **millimeters**, NOT centimeters.
- Correct: `"body_height": 1780` (178 cm × 10)
- Wrong: `"body_height": 178` → triggers 422 error (outside valid range 400–3000 mm)

`body_mass` is in **kilograms**.

Imperial input: set `input_unit_system: "imperial"` — lengths in inches, mass in lbs.
Conversion is applied automatically before validation.

## Anchor sanity bounds (422 error if exceeded)

All values verified against `_ANCHOR_BOUNDS` in `schemas.py`.

| Anchor | Min | Max | Unit |
|--------|-----|-----|------|
| `body_height` | 400 | 3000 | mm |
| `body_mass` | 2 | 400 | kg |
| `foot_length` | 80 | 420 | mm |
| `hand_length` | 60 | 330 | mm |
| `chest_circumference` | 350 | 1800 | mm |
| `knee_height` | 150 | 700 | mm |
| `sitting_height` | 400 | 1300 | mm |
| `span` | 500 | 2900 | mm |
| `trochanterion_height` | 200 | 1200 | mm |
| `hip_circumference` | 300 | 2000 | mm |
| `waist_circumference_omphalion` | 300 | 2000 | mm |
| `neck_circumference` | 150 | 700 | mm |
| `wrist_circumference` | 80 | 400 | mm |
| `head_circumference` | 280 | 720 | mm |
| all other keys | 5 | 3000 | mm |

## Engine routing

`calculation_model: "AUTO"` routes automatically:
- `exact_age` ≤ 20 → PEDIATRIC engine (LMS Box-Cox, CDC/WHO)
- `exact_age` > 20 → ADULT engine (Ridge Regression, ANSUR II)
- If `exact_age` absent, `age_category` determines routing

`exact_age` always takes precedence over `age_category` on conflict.

## Regions (input_origin_region / target_region)

```
GLOBAL | EUROPE | ASIA_PACIFIC | LATAM | INDIA | AFRICA | MIDDLE_EAST
```

Both fields are independent — cross-regional requests are valid.
Example: Asian customer, European brand → `input_origin_region: "ASIA_PACIFIC"`, `target_region: "EUROPE"`

## Anchor strategy (accuracy guide)

| Tier | What you supply | BONE score | FLESH score |
|------|----------------|------------|-------------|
| PRIMARY_RICH | height + mass + ≥1 circumference | ~87 | ~80 |
| PRIMARY_BOTH | height + mass | ~85 | ~78 |
| PRIMARY_ONE | height OR mass (not both) | ~79 | ~62 |
| SECONDARY | foot length, knee height, span, etc. alone | ~74 | ~67 |
| TERTIARY | any other single measurement | ~69 | ~62 |

Precision circumferences for PRIMARY_RICH: `chest_circumference`, `waist_circumference_omphalion`,
`hip_circumference`, `neck_circumference`, `wrist_circumference`

## Bundles

| Bundle | Dimensions | Scope |
|--------|------------|-------|
| `FULL_BODY` | 130 | All available dimensions |
| `HEAD_FACE` | 20 | Head, face, IPD, neck, bridge width |
| `HAND_ARM` | 32 | Fingers, hand, wrist, forearm, arm, reach |
| `TORSO` | 29 | Chest, waist, hip, shoulder breadths, sitting heights |
| `LEGS_FEET` | 34 | Thigh, knee, calf, ankle, foot |

Use `specific_dimensions` array to cherry-pick individual measurements (unions with bundle).

## Body build types

```
CIVILIAN   — NHANES general population (default)
ATHLETIC   — Military/sports lean baseline
OVERWEIGHT — BMI-adjusted circumference morphing for higher body fat
```

## Output interpretation

- `confidence_score > 80`: PRIMARY anchor tier — high reliability
- `range_95`: [lower, upper] 95% prediction interval in output units
- `type: "BONE"`: skeletal landmark (more predictable)
- `type: "FLESH"`: soft tissue — circumferences, depths (higher variance)
- `type: "MEASURED"`: you supplied this as anchor — returned exactly as provided, score = 100
- `biological_limit_status: "OK" | "OUT_OF_BOUNDS"`: NASA-STD-3001 / CDC bounds check

## Pediatric engine

Activate with `exact_age ≤ 20` or a pediatric `age_category`:
```
INFANT (0–2y) | TODDLER (2–4y) | CHILD (4–9y) | PRE_TEEN (9–12y) | TEEN (12–18y)
```

In the pediatric engine, `body_height` and `body_mass` are **outputs** — the CDC LMS method
derives them from age and sex. They appear in `body_dimensions` with confidence 99 (exact
tabular norm). This is the opposite of the adult engine, where they are inputs only and
never appear in `body_dimensions`. Supplying them as anchors overrides the LMS-predicted values.

`head_circumference` is also LMS-derived (confidence 99, available for ages 0–36 months;
older ages clamped to nearest table value).

All Ridge-derived dimensions are capped at confidence score 80.

`header.anchors_calculated` is always `false` for pediatric requests — the LMS method is not
the imputation pipeline. `header.calculated_anchors` is always `{}`.

Minimal pediatric request (no anchors required):
```json
{
  "input_data": {
    "subject": {
      "gender": "female",
      "exact_age": 7.0,
      "age_category": "CHILD"
    },
    "anchors": {}
  }
}
```

## Common 422 errors

```json
// body_height in cm instead of mm
{ "msg": "Value error, 'body_height' = 178.0 mm is outside the valid range [400–3000 mm]." }

// Adult engine with no anchors
{ "msg": "Value error, ADULT engine requires at least one anchor." }

// Invalid region value
{ "msg": "Value error, Invalid input_origin_region 'ANTARKTIDA'." }
```

## Utility endpoints

- `GET /health` — liveness probe, returns `{"status": "healthy", "version": "1.4.0", ...}`
- `GET /v1/info` — all supported enum values (regions, bundles, age categories); safe to cache
- `GET /v1/predict/examples` — 8 ready-to-copy request payloads

## Access

Subscribe on RapidAPI: https://rapidapi.com/d-pot-apps/api/dimensionspot-bodysize-engine
Documentation: https://github.com/D-P0t/dimensionspot-api
