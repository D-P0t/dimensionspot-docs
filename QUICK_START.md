# DimensionsPot - BodySize Engine: **Quick Start**

**DimensionsPot** transforms one or more body measurements into a complete anthropometric
profile of **130 ISO-compliant body dimensions**, each accompanied by a Confidence Score
and a 95% prediction interval.

Supply as little as a single anchor — height, foot length, wrist circumference, or any other
recognized measurement — and the engine reconstructs the full body profile in **under 50 ms**
(typically under 10 ms on a warmed instance). Every dimension includes a calibrated Confidence
Score that is empirically guaranteed never to over-promise: actual prediction accuracy is always
≥ the reported score.

**Two prediction engines, one endpoint:**

| Engine | Method | Training data | Age range |
|--------|--------|---------------|-----------|
| **ADULT** | Ridge Regression + 4-layer Modifier Pipeline | ANSUR II (n = 6,068) | > 20 y |
| **PEDIATRIC** | LMS Box-Cox (CDC) + Ridge hybrid | CDC Growth Charts 2000 (218 age points) | 0–20 y |

Set `calculation_model` to `"AUTO"` (the default) and routing happens automatically based on age.

---

<br>

## Authentication

Subscribe on [RapidAPI](https://rapidapi.com/dimensionspot) and copy your key from the
dashboard. Two headers are required on every request:

```
X-RapidAPI-Key: YOUR_KEY
X-RapidAPI-Host: dimensionspot.p.rapidapi.com
```

---

<br>

## The Request

<br>

### Your First Request

A complete, copy-paste-ready request. All fields are shown with explicit values; defaults are
noted in the Reference section below.

```bash
curl -X POST "https://dimensionspot.p.rapidapi.com/v1/predict" \
  -H "Content-Type: application/json" \
  -H "X-RapidAPI-Key: YOUR_KEY" \
  -H "X-RapidAPI-Host: dimensionspot.p.rapidapi.com" \
  -d '{
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
        "bundle": "FULL_BODY",
        "specific_dimensions": null
      },
      "output_format": {
        "unit_system": "metric",
        "confidence_score_threshold": 0,
        "include_range_95": true,
        "include_iso_codes": true
      }
    }
  }'
```

Same request in Python:

```python
import requests

payload = {
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
        "requested_dimensions": {"bundle": "FULL_BODY"},
        "output_format": {
            "unit_system": "metric",
            "confidence_score_threshold": 0,
            "include_range_95": True,
            "include_iso_codes": True
        }
    }
}

response = requests.post(
    "https://dimensionspot.p.rapidapi.com/v1/predict",
    json=payload,
    headers={
        "X-RapidAPI-Key": "YOUR_KEY",
        "X-RapidAPI-Host": "dimensionspot.p.rapidapi.com"
    }
)
dimensions = response.json()["body_dimensions"]
```

<br>

### Request Field Reference

**`input_data`**

| Field | Required | Default | Allowed values | Description |
|---|---|---|---|---|
| `input_unit_system` | no | `"metric"` | `"metric"` · `"imperial"` | Unit of the anchor values you supply. **Metric:** lengths in mm, mass in kg. **Imperial:** lengths in inches, mass in lbs. Converted to metric before validation. |
| `gender` | **yes** | — | `"male"` · `"female"` | Subject biological sex. |
| `exact_age` | no | `null` | float, 0–120 | Subject age in years. Improves body-composition modifier accuracy. Authoritative engine-routing signal — overrides `age_category` on conflict. |
| `age_category` | no | `"ADULT"` | `"ADULT"` · `"INFANT"` · `"TODDLER"` · `"CHILD"` · `"PRE_TEEN"` · `"TEEN"` | Broad age class. Determines engine when `exact_age` is absent. Any pediatric value forces the Pediatric engine. |
| `input_origin_region` | no | `"GLOBAL"` | see Regions | Population the **input measurements come from**. Normalizes anchors to the ANSUR II global baseline before prediction. |
| `anchors` | **yes (ADULT)** · no (PEDIATRIC) | `{}` | any body measurement key | The measurements you supply. Adult engine requires at least one. Pediatric engine can operate with none. Values in mm (lengths) or kg (body_mass). |

**`output_settings.calculation`**

| Field | Required | Default | Allowed values | Description |
|---|---|---|---|---|
| `calculation_model` | no | `"AUTO"` | `"AUTO"` · `"ADULT"` · `"PEDIATRIC"` | Engine hint. `AUTO` routes by `exact_age` if provided, else by `age_category`. `exact_age` and `age_category` are always the authoritative routing signals regardless of this field. |
| `target_region` | no | `"GLOBAL"` | see Regions | Population to **calibrate output toward**. Independent of `input_origin_region` — you can normalize Asian-origin measurements to European-proportion output. |
| `body_build_type` | no | `"CIVILIAN"` | `"CIVILIAN"` · `"ATHLETIC"` · `"OVERWEIGHT"` | Morphological modifier applied to soft-tissue dimensions. `CIVILIAN` = general population. `ATHLETIC` = military/sports lean baseline. `OVERWEIGHT` = BMI-adjusted NHANES morphing for higher body-fat distribution. |

**`output_settings.requested_dimensions`**

| Field | Required | Default | Allowed values | Description |
|---|---|---|---|---|
| `bundle` | no | `"FULL_BODY"` | `"FULL_BODY"` · `"HEAD_FACE"` · `"HAND_ARM"` · `"TORSO"` · `"LEGS_FEET"` | Filter output to a body region. See Bundles. |
| `specific_dimensions` | no | `null` | list of API keys | Request individual dimensions by API key. Combines with `bundle` as a **union**: all bundle keys + all individually requested keys are returned. Set to `null` or omit to disable. |

**`output_settings.output_format`**

| Field | Required | Default | Allowed values | Description |
|---|---|---|---|---|
| `unit_system` | no | `"metric"` | `"metric"` · `"imperial"` | Output unit. Independent of `input_unit_system`. Metric: mm/kg. Imperial: inches/lbs. |
| `confidence_score_threshold` | no | `0` | integer 0–100 | Suppress dimensions below this Confidence Score. `0` returns all dimensions. |
| `include_range_95` | no | `true` | bool | Include the `[lower, upper]` 95% prediction interval per dimension. |
| `include_iso_codes` | no | `true` | bool | Include the ISO 7250-1:2017 code per dimension (`null` for non-standardized dimensions). |

<br>

### Regions

The same 7 codes apply to both `input_origin_region` and `target_region`.

| Code | Population source | Coverage note |
|---|---|---|
| `GLOBAL` | ANSUR II (US Military baseline) | Full — both genders |
| `EUROPE` | Aggregated European datasets | Full — both genders |
| `ASIA_PACIFIC` | East Asian & Pacific datasets | Full — both genders |
| `LATAM` | Latin American datasets | Full — both genders |
| `INDIA` | South Asian regional data | Female falls back to ASIA_PACIFIC — noted in `meta_warnings` |
| `AFRICA` | Sub-Saharan and regional proxy data | Male-only, −10 % confidence penalty — noted in `meta_warnings` |
| `MIDDLE_EAST` | Middle Eastern regional data | Validated for males 18–30 only — no runtime `meta_warnings` emitted |

<br>

### Bundles

| Bundle | Dimensions | Scope |
|---|---|---|
| `FULL_BODY` | 130 | All available dimensions |
| `HEAD_FACE` | 20 | Head, face, interpupillary distance, neck, bridge width |
| `HAND_ARM` | 32 | Fingers, hand, wrist, forearm, arm, reach |
| `TORSO` | 29 | Chest, waist, hip, shoulder breadths, sitting heights |
| `LEGS_FEET` | 34 | Thigh, knee, calf, ankle, foot |

> Some dimensions appear in more than one named bundle (e.g., `neck_circumference` in both
> HEAD_FACE and TORSO; `knee_height`, `popliteal_height`, `trochanterion_height` in both
> TORSO and LEGS_FEET). 19 dimensions are FULL_BODY-only and do not belong to any named bundle.
>
> For a complete list of all 130 dimension keys with anatomical descriptions, ISO codes, and
> bundle membership, see the [Data Dictionary →](DATA_DICTIONARY.md).

**Combining `bundle` and `specific_dimensions`:**

When both are provided, their results are **unioned** — not intersected:

```json
"requested_dimensions": {
  "bundle": "HAND_ARM",
  "specific_dimensions": ["shoulder_height", "waist_circumference_natural"]
}
```

This returns all 32 HAND_ARM dimensions plus `shoulder_height` and `waist_circumference_natural`.
Useful when you need a region-focused bundle with a few extra dimensions from another region.

<br>

### Engine Routing

```
IF exact_age is provided:
    exact_age ≤ 20 y  →  PEDIATRIC engine
    exact_age > 20 y  →  ADULT engine
    If exact_age and age_category disagree → warning in meta_warnings; exact_age wins

IF exact_age is absent:
    age_category ∈ {INFANT, TODDLER, CHILD, PRE_TEEN, TEEN}  →  PEDIATRIC engine
    age_category = ADULT  →  ADULT engine
    Warning in meta_warnings stating the assumed age used by body-composition modifiers
```

`exact_age` is always authoritative. When only `age_category` is available, the engine uses the
category median as the assumed age for body-composition calculations (not for CDC growth tables).
Providing `exact_age` eliminates this uncertainty entirely.

<br>

### Anchor Mechanics and Imputation

Any recognized body measurement key is a valid anchor. The adult engine requires at least one
anchor and accepts any number — accuracy improves with each additional anchor and plateaus
after the PRIMARY_RICH tier (height + mass + one precision circumference).

**Anchor sanity bounds** — values outside these ranges produce a `422` error:

| Anchor | Min | Max | Unit |
|---|---|---|---|
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

All lengths and circumferences must be in **mm**. `body_mass` in **kg**. If you supply imperial
values, set `input_unit_system: "imperial"` and conversion is applied before validation.

**Dynamic Imputation:**
When `body_height` or `body_mass` are absent, the imputer reconstructs them from whatever anchor
you supply using a dedicated Ridge model trained on ANSUR II. The imputed values appear in the
response header as `calculated_anchors`, and a confidence penalty proportional to imputation
uncertainty (up to −10 points) is applied to all output scores.

```json
"anchors": { "foot_length": 275 }
```

The imputer infers `body_height` and `body_mass`, runs the full 130-dimension pipeline, and
reports `"anchors_calculated": true` in the response header.

<br>

### Imperial Input

Set `input_unit_system: "imperial"` when your anchor values are in inches and lbs:

```bash
curl -X POST "https://dimensionspot.p.rapidapi.com/v1/predict" \
  -H "Content-Type: application/json" \
  -H "X-RapidAPI-Key: YOUR_KEY" \
  -H "X-RapidAPI-Host: dimensionspot.p.rapidapi.com" \
  -d '{
    "input_data": {
      "input_unit_system": "imperial",
      "subject": {
        "gender": "female",
        "exact_age": 28.0,
        "age_category": "ADULT",
        "input_origin_region": "GLOBAL"
      },
      "anchors": {
        "body_height": 64.0,
        "body_mass": 130.0
      }
    },
    "output_settings": {
      "output_format": {
        "unit_system": "imperial"
      }
    }
  }'
```

Conversion applied automatically before validation:
- `body_mass`: lbs ÷ 2.20462 → kg
- all lengths and circumferences: inches × 25.4 → mm

`output_format.unit_system` controls the **output** units and is independent of the input
conversion.

<br>

### Minimum Valid Request

For adult subjects, `gender` plus one anchor is the minimum. All `output_settings` fields have
defaults and can be omitted.

```json
{
  "input_data": {
    "subject": { "gender": "male" },
    "anchors": { "body_height": 1780 }
  }
}
```

This returns all 130 FULL_BODY dimensions in metric with 95% intervals and ISO codes.

<br>

### Pediatric Requests

Activate the pediatric engine with a pediatric `age_category` or an `exact_age ≤ 20`.

```json
{
  "input_data": {
    "subject": {
      "gender": "female",
      "exact_age": 7.0,
      "age_category": "CHILD",
      "input_origin_region": "GLOBAL"
    },
    "anchors": {}
  },
  "output_settings": {
    "calculation": {
      "calculation_model": "AUTO",
      "target_region": "GLOBAL",
      "body_build_type": "CIVILIAN"
    },
    "requested_dimensions": { "bundle": "HEAD_FACE" },
    "output_format": {
      "unit_system": "metric",
      "confidence_score_threshold": 0,
      "include_range_95": true,
      "include_iso_codes": false
    }
  }
}
```

> **Important:** In the pediatric engine, `body_height` and `body_mass` are **outputs**, not
> inputs. The CDC LMS method predicts them from age and sex, then uses them as a scaling base
> for the full 130-dimension skeleton via the adult Ridge model. If you supply `body_height`
> or `body_mass` as anchors, they take precedence over the CDC-predicted values.

**Pediatric age categories:**

| `age_category` | Typical range | Assumed age (when `exact_age` absent) | Engine |
|---|---|---|---|
| `INFANT` | 0–2 y | 1.0 y | LMS + Ridge hybrid |
| `TODDLER` | 2–4 y | 3.0 y | LMS + Ridge hybrid |
| `CHILD` | 4–9 y | 6.5 y | LMS + Ridge hybrid |
| `PRE_TEEN` | 9–12 y | 10.5 y | LMS + Ridge hybrid |
| `TEEN` | 12–18 y | 15.0 y | LMS + Ridge hybrid |
| `ADULT` | 18 + | population mean (35 y) | Ridge Regression |

`exact_age` is strongly recommended for pediatric subjects — growth rates are high and the
assumed category median may not represent the subject well.

**Known pediatric limitations:**
- Confidence scores for all Ridge-derived dimensions are capped at **80** (LMS-derived
  dimensions — `body_height`, `body_mass`, `head_circumference` — keep their own scores).
- `head_circumference`: CDC data covers ages 0–36 months. Older ages are clamped to the
  nearest available value.

---

<br>

## The Response

<br>

### Response Anatomy

```json
{
  "header": {
    "status": "success",
    "calculation_model_used": "ADULT",
    "anchors_calculated": false,
    "calculated_anchors": {},
    "modifiers_applied": [
      "Regional Calibration (EUROPE)",
      "Civilian Body Composition (BF%=22.9%, delta=0.3%, body_type=CIVILIAN)"
    ],
    "meta_warnings": []
  },
  "body_dimensions": {
    "shoulder_height": {
      "label": "Shoulder Height",
      "description": "Vertical distance from the floor to the acromion landmark. Used in workstation design, doorway clearance, and reach-zone ergonomics.",
      "value": 1426.89,
      "unit": "mm",
      "type": "BONE",
      "confidence_score": 85,
      "range_95": [1397.09, 1456.70],
      "iso_code": "6.1.4",
      "biological_limit_status": "OK"
    },
    "hip_circumference": {
      "label": "Hip Circumference",
      "description": "Maximum horizontal circumference around the buttocks. Primary sizing dimension for trousers, skirts, and fitted garments.",
      "value": 1003.41,
      "unit": "mm",
      "type": "FLESH",
      "confidence_score": 78,
      "range_95": [921.14, 1085.68],
      "iso_code": null,
      "biological_limit_status": "OK"
    }
  },
  "system_info": {
    "api_version": "v1",
    "model_version": "adult_ridge_v4.0",
    "computation_time_ms": 18
  }
}
```

> The `body_dimensions` object contains up to 130 entries for a FULL_BODY request.
>
> **About `MEASURED` type:** `body_height` and `body_mass` are input features for the adult
> Ridge model and do not appear as entries in `body_dimensions`. However, any anchor that is
> also a prediction target — such as `wrist_circumference`, `hip_circumference`, or
> `foot_length` — will appear with `"type": "MEASURED"`, `confidence_score: 100`, and its
> value set exactly to what you provided. The `range_95` for such entries reflects the model's
> own prediction interval, which can serve as a plausibility check on the supplied measurement.

<br>

### `header` Field Reference

| Field | Type | Description |
|---|---|---|
| `status` | string | `"success"` — at least one dimension returned. `"partial_success"` — all dimensions were filtered out (e.g., `confidence_score_threshold` set too high, or engine produced no output). |
| `calculation_model_used` | string | `"ADULT"` or `"PEDIATRIC"` — the engine that handled the request. |
| `anchors_calculated` | bool | `true` if any anchor (`body_height` or `body_mass`) was imputed from secondary measurements. |
| `calculated_anchors` | object | Key/value pairs of imputed anchor keys and their inferred values (always in metric units, regardless of `output_format.unit_system`). Empty when `anchors_calculated` is `false`. |
| `modifiers_applied` | list | Post-prediction pipeline steps applied — regional calibration, body-composition morphing, anatomical enrichment. |
| `meta_warnings` | list | Non-fatal informational notices. See triggers below. |

**`meta_warnings` are generated when:**

- **`exact_age` absent** — the assumed age used by body-composition modifiers is stated explicitly.
- **Age conflict** — `exact_age` and `age_category` disagree on engine selection; the winning signal and overridden value are named.
- **Regional data limitation** — partial coverage for `AFRICA` or `INDIA`; a confidence penalty is applied and the penalty amount is described. (`MIDDLE_EAST` has a documented static limitation but does not emit a runtime warning.)
- **Data quality flag** — pipeline-detected anomaly (e.g., BMI outside a plausible range for the supplied height/mass combination).

<br>

### `body_dimensions` Entry Field Reference

| Field | Type | Description |
|---|---|---|
| `label` | string | Human-readable dimension name (e.g., `"Shoulder Height"`). |
| `description` | string | Anatomical definition of the landmark, with commercial application context. `null` if no description entry exists. |
| `value` | float | Predicted value in the requested output unit. |
| `unit` | string | `"mm"` or `"inch"` for lengths/circumferences; `"kg"` or `"lb"` for `body_mass`. |
| `type` | string | Measurement provenance — see type values below. |
| `confidence_score` | integer | Heuristic reliability index [0–100] — see Confidence Score section. |
| `range_95` | list or null | `[lower, upper]` 95% prediction interval in output units. `null` when `include_range_95: false`. |
| `iso_code` | string or null | ISO 7250-1:2017 section code. `null` for non-standardized dimensions, or when `include_iso_codes: false`. |
| `biological_limit_status` | string | NASA-STD-3001 / CDC bounds check — see status values below. |

**`type` values:**

| Value | Meaning |
|---|---|
| `BONE` | Skeletal/structural dimension. Higher inherent accuracy; less sensitive to body-composition variation. |
| `FLESH` | Soft-tissue dimension (circumferences, depths). Lower inherent accuracy; varies with body fat and musculature. |
| `MEASURED` | Value was supplied by the caller as an anchor. Returned exactly as provided; `confidence_score` is always 100. Never overwritten by the model. |

**`biological_limit_status` values:**

| Value | Meaning |
|---|---|
| `OK` | Within the valid population range. |
| `OUT_OF_BOUNDS` | Outside the valid range — either below the minimum or above the maximum. For adults: NASA-STD-3001 absolute limits. For pediatric subjects: age-banded CDC P1/P99 limits. |

`OUT_OF_BOUNDS` does not suppress a dimension from the output — it is an informational flag.
It typically appears when input anchors describe an extreme body type, or when an anchor
combination is biomechanically unusual (e.g., very large wrist circumference with average height).

<br>

### Confidence Score

`confidence_score` is an empirically calibrated, anchor-tier-based reliability index. It is
**deterministic**: given the same set of anchor keys (not values) and tissue type, the score
is always the same. It is never over-reported — the gap between stated and actual prediction
accuracy is always ≥ 0.

**Tier classification** is determined from the raw anchor keys you provide, before any
imputation occurs:

| Tier | Anchor condition | BONE score | FLESH score |
|---|---|---|---|
| **PRIMARY_RICH** | `body_height` + `body_mass` + ≥ 1 precision anchor | **87** | **80** |
| **PRIMARY_BOTH** | `body_height` + `body_mass` | **85** | **78** |
| **PRIMARY_ONE** | `body_height` **or** `body_mass` (not both) | **79** | **62** |
| **SECONDARY** | one strong secondary anchor (no primary) | **74** | **67** |
| **TERTIARY** | any other single anchor | **69** | **62** |

**Precision anchors** (any one of these combined with `body_height` + `body_mass` elevates
the tier from PRIMARY_BOTH → PRIMARY_RICH):

```
hip_circumference  ·  waist_circumference_omphalion  ·  chest_circumference
neck_circumference  ·  wrist_circumference
```

**Secondary anchors** (classify as SECONDARY tier when used alone without primary anchors):

```
foot_length  ·  hand_length  ·  chest_circumference  ·  knee_height
sitting_height  ·  span  ·  trochanterion_height  ·  hip_circumference
waist_circumference_omphalion  ·  neck_circumference  ·  wrist_circumference
```

**Why PRIMARY_ONE FLESH = 62** (not the expected ~75):
When only one primary anchor is available — height without weight, or weight without height —
circumference predictions are particularly uncertain because body composition (the main driver
of soft-tissue dimensions) cannot be inferred without both anchors. The score is conservatively
set to 62, reflecting the empirically measured 95-PI coverage floor of 66.1% for this scenario.

**Imputation penalty:**
When missing anchors are imputed, scores decrease by up to **10 additional points** proportional
to imputation uncertainty. The imputed values and their confidence penalty are reported in the
response header (`calculated_anchors`).

**Pediatric engine:**
All Ridge-derived dimensions are capped at **80** when the pediatric hybrid engine is active.
LMS-derived dimensions (`body_height`, `body_mass`, `head_circumference`) retain their own score of **99** (exact tabular norm, not a regression estimate).

> **Guarantee:** `confidence_score` is a proprietary heuristic reliability index, not a
> frequentist probability. For every dimension at every tier, actual 95-PI coverage on held-out
> ANSUR II data is ≥ the reported score. The stated floor for PRIMARY_RICH BONE is 87%, for
> PRIMARY_RICH FLESH is 80% — both validated against n=300 precision validation runs.

<br>

### `system_info` Field Reference

| Field | Description |
|---|---|
| `api_version` | API version prefix (`"v1"`). |
| `model_version` | Model identifier: `"adult_ridge_v4.0"` (ADULT engine) or `"v1.3_lms_cdc_age_banded"` (PEDIATRIC engine). |
| `computation_time_ms` | Total server-side processing time in milliseconds. |

---

<br>

## Error Reference

| HTTP | Trigger | Response body |
|---|---|---|
| `422` | Validation error — invalid enum value, negative anchor, out-of-range age, missing required field, anchor outside sanity bounds, adult engine called with empty anchors. | Standard FastAPI `detail` array with `loc`, `msg`, and `input`. |
| `403` | Request reached the backend directly, bypassing the RapidAPI gateway. | `{"error": "forbidden", "message": "..."}` |
| `500` | Internal engine error. | `{"error": "internal_server_error", "message": "..."}` |

**Common `422` payloads:**

```json
// Invalid region  (field_validator → "Value error, " prefix)
{ "msg": "Value error, Invalid input_origin_region 'ANTARKTIDA'." }

// Anchor in cm instead of mm  (body_height must be 400–3000 mm)
{ "msg": "Value error, 'body_height' = 178.0 mm is outside the valid range [400–3000 mm]. All lengths and circumferences must be in mm; body_mass in kg." }

// Adult engine with no anchors
{ "msg": "Value error, ADULT engine requires at least one anchor." }

// exact_age out of range  (Pydantic type constraint, no "Value error" prefix)
{ "msg": "Input should be less than or equal to 120" }

// Negative anchor value
{ "msg": "Value error, Measurement 'body_height' must be strictly positive (got -150.0)." }
```

The most common production error is submitting `body_height` in centimetres (e.g., `178.0`)
instead of millimetres (`1780`). The sanity bounds catch this immediately with a descriptive
error message.

---

<br>

## Utility Endpoints

**`GET /health`** — Liveness / readiness probe

```bash
curl https://dimensionspot.p.rapidapi.com/health \
  -H "X-RapidAPI-Key: YOUR_KEY"
```

Returns `200` when all critical runtime dependencies are available. Returns `503` when any
are missing — container orchestrators use this to pause traffic until the instance is ready.

```json
{
  "status": "healthy",
  "version": "1.4.0",
  "models_loaded": true,
  "data_files_ok": true,
  "uptime_seconds": 3721
}
```

<br>

**`GET /v1/info`** — Capability discovery

```bash
curl https://dimensionspot.p.rapidapi.com/v1/info \
  -H "X-RapidAPI-Key: YOUR_KEY"
```

Returns all supported enum values (regions, bundles, age categories, body build types,
calculation models, unit systems), model version identifiers, biological limits metadata,
and the full endpoint map. The result does not change at runtime — safe to cache in your client.
Use it for programmatic enum validation instead of hardcoding allowed values.

<br>

**`GET /v1/predict/examples`** — Pre-built request payloads

```bash
curl https://dimensionspot.p.rapidapi.com/v1/predict/examples \
  -H "X-RapidAPI-Key: YOUR_KEY"
```

Returns 8 ready-to-use request payloads covering the main use cases:

| # | Scenario |
|---|---|
| 1 | Strong anchors — height + weight |
| 2 | Rich anchors — height + weight + ≥1 circumference |
| 3 | Single anchor — one secondary anchor only |
| 4 | Targeted dimensions — returns selected dimensions only |
| 5 | Bundle filter — returns dimensions from selected bundle only |
| 6 | Regional calibration — output normalised to selected region |
| 7 | Body build type — output morphed to selected body type |
| 8 | Pediatric model — applies LMS + Ridge hybrid |

Copy any `payload` field directly into `POST /v1/predict`. In Swagger UI (`/docs`), the same
examples appear in the **Examples** dropdown on the predict endpoint — no copy-paste needed.

<br>

**`GET /docs`** — Swagger UI

```
https://dimensionspot.p.rapidapi.com/docs
```

Full OpenAPI interface with inline schema explorer, all 8 examples pre-loaded in the dropdown,
and live **Try it out** execution. The fastest way to explore the API without writing any code.
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
