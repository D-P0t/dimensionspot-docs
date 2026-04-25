# Wearables — Band, Ring & Ankle Fit

<br>

## Business Context

**The Problem:** Wearable returns share a single root cause: the device didn't fit. S/M/L guidance on a product page doesn't get read. A loose band corrupts the optical signal, and the user blames the sensor. A smart ring that's off by one size ships back by day three. Bracket-ordering is still standard practice in the category, and the reverse logistics bill and the sizing-kit budget are the same problem on different SKUs.

**The Solution:** Replace the sizing kit with a short prompt at size selection. DimensionsPot takes the height and weight your customer will share when there's a clear reason to, and returns wrist, hand, ankle, and finger dimensions — including the PIP joint width that actually determines ring size — in under 10ms. No camera, no PII. The correct size variant drops into the picking list before the order leaves the warehouse.

**The Boundary Safety Net:** Every dimension ships with a 95% prediction interval. When a predicted value lands near a size threshold, both adjacent sizes surface automatically in the UI. The customer chooses based on fit preference ("I like my ring a little loose"), not a blind guess.

<br>

## Recommended API Configuration

| Parameter | Value | Reason |
|---|---|---|
| `anchors` | `body_height` + `body_mass` | PRIMARY_BOTH tier — FLESH dims ~78, BONE dims ~85 |
| `bundle` | `HAND_ARM` | Returns all 32 hand and arm dimensions including wrist, hand, and all finger dimensions |
| `body_build_type` | `CIVILIAN` | General consumer population |
| `confidence_score_threshold` | `70` | Captures all wrist and hand FLESH dims (~78) and finger BONE dims (~75) while filtering genuinely uncertain outputs |
| `target_region` | Customer's region | Regional calibration has measurable effect on wrist and hand norms, particularly for `ASIA_PACIFIC` |

> **Single-anchor note:** If only height is available (no weight), use `anchors: {"body_height": <value>}`. The engine imputes `body_mass` via Ridge regression (PRIMARY_ONE tier). `wrist_circumference` confidence drops to ~62 — sufficient for S/M/L band routing, but always surface both adjacent sizes when the predicted value sits near a threshold.

<br>

## Key Dimensions for Wearables

### Wrist & arm:

| API Key | Label | Type | MAE (mm) | Use |
|---|---|---|---|---|
| `wrist_circumference` | Wrist Circumference | FLESH | ~5 | Smartwatch / fitness tracker band sizing |
| `wrist_breadth` | Wrist Breadth | BONE | — | Watch lug-to-lug fit; band clasp width |
| `forearm_circumference` | Forearm Circumference | FLESH | ~12 | Forearm band and sleeve sizing |

### Hand & fingers:

| API Key | Label | Type | MAE (mm) | Use |
|---|---|---|---|---|
| `hand_circumference` | Hand Circumference | FLESH | ~7 | Smart ring broad sizing proxy; glove fit |
| `hand_breadth` | Hand Breadth | BONE | ~3 | Glove width; haptic device sizing |
| `hand_length` | Hand Length | BONE | ~7 | Glove total length; haptic device palm coverage |
| `palm_length` | Palm Length | BONE | ~5 | Glove palm panel length |
| `hand_digit_4_width_pip` | Ring Finger Width (PIP) | BONE | — ‡ | Smart ring precise sizing — PIP is the joint the ring must pass over |
| `hand_digit_4_length` | Ring Finger Length | BONE | — ‡ | Ring band width / coverage zone |
| `hand_digit_1_width_ip` | Thumb Width (IP) | BONE | — ‡ | Thumb ring sizing |

> **‡ Finger dimensions** are derived via validated Greiner skeletal proportion ratios from `hand_length` and carry a −10% confidence adjustment relative to directly modelled dimensions. They are not directly validated in the regression test suite but are internally consistent with the hand model.

> All five fingers have PIP and DIP widths available (`hand_digit_1` through `hand_digit_5`). The full set is returned by the `HAND_ARM` bundle automatically.

### Ankle:

| API Key | Label | Type | MAE (mm) | Use |
|---|---|---|---|---|
| `ankle_circumference` | Ankle Circumference | FLESH | ~11 | Ankle tracker and GPS tag sizing |

> `ankle_circumference` is in the `LEGS_FEET` bundle. To retrieve it alongside hand and wrist dimensions in one call, add `"ankle_circumference"` to `specific_dimensions` while keeping `bundle: "HAND_ARM"`.

<br>
<br>

## Sample Request — Full Hand & Wrist Profile (height + weight)

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
        "exact_age": 34.0,
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
        "bundle": "HAND_ARM",
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

## Sample Request — Height-Only (single anchor)

For checkout flows that collect only height:

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
        "exact_age": 34.0,
        "age_category": "ADULT",
        "input_origin_region": "EUROPE"
      },
      "anchors": {
        "body_height": 1680.0
      }
    },
    "output_settings": {
      "calculation": {
        "calculation_model": "AUTO",
        "target_region": "EUROPE",
        "body_build_type": "CIVILIAN"
      },
      "requested_dimensions": {
        "bundle": "HAND_ARM",
        "specific_dimensions": null
      },
      "output_format": {
        "unit_system": "metric",
        "confidence_score_threshold": 60,
        "include_range_95": true,
        "include_iso_codes": false
      }
    }
  }'
```

When only `body_height` is provided, `anchors_calculated: true` appears in the response header and `body_mass` is listed under `calculated_anchors`. The anchor tier is PRIMARY_ONE — `wrist_circumference` (FLESH) carries confidence ~62.

<br>

## Band Size Mapping

Map `wrist_circumference` to standard band sizes client-side:

```python
BAND_SIZES = [
    (0,   150, "XS"),
    (150, 165, "S"),
    (165, 185, "M"),
    (185, 205, "L"),
    (205, 999, "XL"),
]

def lookup_band_size(wrist_mm):
    for lo, hi, label in BAND_SIZES:
        if lo <= wrist_mm < hi:
            return label
    return "Unknown"

wrist_dim = response["body_dimensions"]["wrist_circumference"]
wrist     = wrist_dim["value"]
lower_95  = wrist_dim["range_95"][0]
upper_95  = wrist_dim["range_95"][1]

size       = lookup_band_size(wrist)
size_lower = lookup_band_size(lower_95)
size_upper = lookup_band_size(upper_95)

if size_lower != size_upper:
    print(f"Between sizes: try {size_lower} or {size} — choose based on fit preference")
else:
    print(f"Recommended band size: {size}")
```

<br>

## Smart Ring Sizing Pattern

The API provides two complementary signals for ring sizing.

**Broad sizing — `hand_circumference`** correlates with overall hand size and maps to brand size systems (XS–XL or numeric). Use this as the primary routing signal:

```python
RING_SIZES_BY_HAND_CIRC = [
    (0,    170, "XS"),   # approx US 5–6
    (170,  185, "S"),    # approx US 6–7
    (185,  200, "M"),    # approx US 7–8
    (200,  215, "L"),    # approx US 8–9
    (215,  230, "XL"),   # approx US 9–10
    (230,  999, "XXL"),  # approx US 10+
]

def lookup_ring_size(hand_circ_mm):
    for lo, hi, label in RING_SIZES_BY_HAND_CIRC:
        if lo <= hand_circ_mm < hi:
            return label
    return "Unknown"

hand_dim  = response["body_dimensions"]["hand_circumference"]
hand_circ = hand_dim["value"]
lower_95  = hand_dim["range_95"][0]
upper_95  = hand_dim["range_95"][1]

size       = lookup_ring_size(hand_circ)
size_lower = lookup_ring_size(lower_95)
size_upper = lookup_ring_size(upper_95)

if size_lower != size_upper:
    print(f"Between sizes: try {size_lower} or {size}")
else:
    print(f"Recommended ring size: {size}")
```

**Precise sizing — `hand_digit_4_width_pip`** is the anatomical width of the ring finger at the PIP joint — the widest point the ring must pass over. This is the standard anatomical measurement used to determine ring size. Convert width to estimated circumference and look up the corresponding ring size:

```python
import math

# Ring finger PIP width → estimated circumference → US ring size
# Assumes approximately circular finger cross-section at PIP joint
RING_SIZES_BY_PIP = [
    # (pip_width_min_mm, pip_width_max_mm, US_size, ISO_circ_mm)
    (0,    15.6, "5",  "49"),
    (15.6, 16.5, "6",  "52"),
    (16.5, 17.3, "7",  "54"),
    (17.3, 18.1, "8",  "57"),
    (18.1, 19.0, "9",  "60"),
    (19.0, 19.8, "10", "62"),
    (19.8, 999,  "11+", "65+"),
]

def lookup_ring_size_by_pip(pip_width_mm):
    for lo, hi, us_size, iso_circ in RING_SIZES_BY_PIP:
        if lo <= pip_width_mm < hi:
            return us_size, iso_circ
    return "Unknown", None

dims = response["body_dimensions"]
pip_width = dims["hand_digit_4_width_pip"]["value"]
us_size, iso_circ = lookup_ring_size_by_pip(pip_width)

# Estimated circumference for display
est_circ_mm = round(pip_width * math.pi, 1)
print(f"Ring finger PIP width: {pip_width:.1f} mm")
print(f"Estimated circumference: ~{est_circ_mm} mm")
print(f"Suggested US ring size: {us_size}  |  ISO: {iso_circ} mm")
```

> **Two-signal approach:** Use `hand_circumference` for initial size routing. Use `hand_digit_4_width_pip` for confirmation or when your size system is based on individual ring size (numeric US/ISO). When both signals point to the same size, confidence is high. When they diverge by one step, surface both and let the customer choose.

> Finger cross-section is not perfectly circular — the circumference estimate from width alone has inherent approximation error. Validate the `hand_digit_4_width_pip` → ring size mapping against your own measured data before deploying at scale.

<br>

## Response Handling Tips

- **Height + weight** (PRIMARY_BOTH): `wrist_circumference` ~78 confidence, `hand_breadth` and `hand_circumference` similar — sufficient for confident single-size routing. Use `range_95` to surface boundary cases.
- **Height only** (PRIMARY_ONE): `wrist_circumference` drops to ~62 confidence — adequate for S/M/L triage, but always surface both adjacent sizes when the predicted value sits within 5 mm of a threshold.
- `wrist_breadth` (BONE, ~85 confidence) is the bony wrist width across the distal radius/ulna — use it for watch lug-to-lug clearance and band clasp width, not for circumference-based band sizing.
- Finger dimensions (`hand_digit_*`) carry a −10% confidence adjustment relative to directly modelled dimensions. They are derived via Greiner ratios from `hand_length` and are internally consistent with the full hand model. Use `range_95` on `hand_digit_4_width_pip` to detect boundary cases in ring sizing.
- Regional calibration has a measurable effect on wrist and hand norms. Always set `target_region` to the customer's region. For `ASIA_PACIFIC`, wrist circumference norms differ from the ANSUR II baseline by up to 8–12 mm — using `GLOBAL` as default will produce systematically wrong size recommendations for Asian customers.
- Flag any dimension with `biological_limit_status: "OUT_OF_BOUNDS"` before using it in size routing — out-of-bounds values fall outside population normal range and should prompt the customer to contact support rather than triggering an automated recommendation.
- For ankle tracking devices, add `"ankle_circumference"` to `specific_dimensions` rather than switching to `FULL_BODY` — the HAND_ARM bundle covers hand and wrist, and a targeted `specific_dimensions` call avoids the larger FULL_BODY payload.
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
