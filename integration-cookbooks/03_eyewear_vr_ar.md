# Online Eyewear & VR/AR — Head & Face Fit Engine

<br>

## Business Context

**The Problem:** Frame fit is the single largest return driver in online optical. Customers don't know their face width, bridge size, or whether a temple length will pinch behind the ear — so they bracket-buy across sizes, and the ones who don't bracket tend to return. On the VR/AR side, a strap that's 10mm too tight causes pressure headaches, and a light seal that doesn't match face depth leaks light and breaks immersion. Virtual try-on solves the aesthetic question; it doesn't solve fit.

**The Solution:** Two numbers most customers already know — height and weight — captured at the point of size selection. DimensionsPot takes those two inputs and returns up to 24 precise head and face dimensions in under 10ms. No cameras, no scans, no PII. One API call tells you which frame front width fits the face, which temple length reaches behind the ears, and which headset strap size matches the customer's head circumference. The customer walks away from the product page believing they picked the right size the first time.

**The Customization Edge:** The real margin move happens between order and dispatch. Route the order to the correct temple length SKU, select the Asian-fit or standard rim based on facial proportions, and ship the headset with the matching light-seal cushion already installed. Same checkout, fewer returns, higher fulfilment accuracy — driven by two fields and one API call.

<br>

## Recommended API Configuration

| Parameter | Value | Reason |
|---|---|---|
| `anchors` | `body_height` + `body_mass` | PRIMARY_BOTH tier — skeletal HEAD_FACE BONE dims ~85 confidence |
| `bundle` | `HEAD_FACE` | Returns all 20 head and face dimensions |
| `body_build_type` | `CIVILIAN` | Standard population |
| `confidence_score_threshold` | `0` | Receive all 20 dims and filter client-side by use case |
| `include_range_95` | `true` | Required for boundary detection at frame size thresholds |

> **Regional calibration is critical for head and face dimensions.** East Asian and South Asian populations have measurably different head breadth, nasal bridge depth, and bizygomatic breadth relative to the ANSUR global baseline. The sizing error from using the wrong region is proportionally larger for facial dimensions than for body dimensions. Always set `input_origin_region` and `target_region` correctly.

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
        "exact_age": 35.0,
        "age_category": "ADULT",
        "input_origin_region": "ASIA_PACIFIC"
      },
      "anchors": {
        "body_height": 1740.0,
        "body_mass": 72.0
      }
    },
    "output_settings": {
      "calculation": {
        "calculation_model": "AUTO",
        "target_region": "ASIA_PACIFIC",
        "body_build_type": "CIVILIAN"
      },
      "requested_dimensions": {
        "bundle": "HEAD_FACE",
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

<br>

## Key Dimensions for Eyewear & VR/AR

| API Key | Label | Type | Use |
|---|---|---|---|
| `head_breadth` | Head Breadth | BONE | Frame front width sizing; temple length guide; VR shell width |
| `bizygomatic_breadth` | Cheekbone Breadth | BONE | Frame front width selection; cheek clearance |
| `face_length` | Face Length | BONE | Frame vertical depth; lens height selection |
| `head_circumference` | Head Circumference | FLESH | VR/AR headset strap size; hat and helmet sizing |
| `head_length` | Head Length | BONE | VR headset front-to-back depth; helmet sizing |
| `bitragion_coronal_arc` | Bitragion Coronal Arc | BONE | Over-head strap length; VR head strap tensioning |
| `bitragion_frontal_arc` | Bitragion Frontal Arc | BONE | Forehead strap width; AR/VR brow pad sizing |
| `bridge_width` | Bridge Width | BONE | Frame bridge size — pad-corrected value for frame specification |
| `nasal_root_breadth` | Nasal Root Breadth | BONE | Asian-fit vs standard routing; AR/VR nose-rest geometry |
| `menton_sellion_length` | Face Depth | BONE | VR light-seal cushion depth; face shield front clearance |
| `maximum_frontal_breadth` | Maximum Frontal Breadth | BONE | Helmet and headset brow width |
| `neck_circumference` | Neck Circumference | FLESH | Helmet chin-strap sizing; neckband wearables |
| `ear_protrusion` ‡ | Ear Protrusion | BONE | VR/AR ear cup depth clearance — how far the ear projects from the head |
| `ear_length` ‡ | Ear Length | BONE | Earbud and in-ear device sizing; BTE hearing aid retention arm |
| `ear_breadth` ‡ | Ear Breadth | BONE | Custom ear mould sizing; earphone cushion shape |
| `tragion_top_of_head` ‡ | Tragion-Top of Head | BONE | VR headset vertical crown height; helmet shell interior height |

> **‡ FULL_BODY only.** The four ear and head-height dimensions are not returned by `bundle: "HEAD_FACE"`. To retrieve them alongside the 20 HEAD_FACE dimensions in a single call, either use `bundle: "FULL_BODY"` or list all needed keys explicitly in `specific_dimensions`.

> **`bridge_width`** is derived from `nasal_root_breadth` with a −4 mm correction for standard 2 mm nose pad contact points. Use `bridge_width` for frame bridge size specification in UI and order routing. Use `nasal_root_breadth` directly for Asian-fit detection logic and AR/VR nose-rest 3D geometry.

<br>

## Frame Size Recommendation Pattern

Map head and face dimensions to frame width, height, temple length, and bridge size:

```python
def recommend_frame(dims):
    """
    Returns frame width category, height category, bridge size,
    and temple length guidance from API head/face dimensions.
    Thresholds are indicative — adjust to your frame catalogue.
    """
    head_breadth = dims["head_breadth"]["value"]          # mm
    face_length  = dims["face_length"]["value"]           # mm
    bizygomatic  = dims["bizygomatic_breadth"]["value"]   # mm
    bridge       = dims["bridge_width"]["value"]          # mm

    # Frame front width (bizygomatic breadth + cheek clearance)
    if bizygomatic < 130:
        width_cat = "narrow"     # frame front ~120–130 mm
    elif bizygomatic < 142:
        width_cat = "medium"     # frame front ~130–142 mm
    else:
        width_cat = "wide"       # frame front ~142–155 mm

    # Frame vertical height (face length)
    if face_length < 112:
        height_cat = "short"     # lens height ~38–42 mm
    elif face_length < 124:
        height_cat = "medium"    # lens height ~42–48 mm
    else:
        height_cat = "tall"      # lens height ~48–55 mm

    # Temple length (head breadth proxy)
    # Standard temple lengths: 135, 140, 145 mm
    if head_breadth < 148:
        temple_mm = 135
    elif head_breadth < 158:
        temple_mm = 140
    else:
        temple_mm = 145

    return {
        "frame_width_category":       width_cat,
        "frame_height_category":      height_cat,
        "bridge_size_mm":             round(bridge),
        "recommended_temple_length_mm": temple_mm,
    }

dims = response["body_dimensions"]
frame = recommend_frame(dims)
```

Use `range_95` to catch boundary cases: if `bizygomatic_breadth` or `face_length` sits within 3–4 mm of a threshold, surface both adjacent size options rather than a single recommendation.

<br>

## Asian-Fit Detection Pattern

Asian-fit frames use a raised nose bridge (or no nose pads), a wider front, and adjusted temple angles. Route orders to the correct SKU variant using `nasal_root_breadth` as the anatomical signal, with `input_origin_region` as a supporting indicator:

```python
def detect_asian_fit(dims, input_origin_region):
    """
    Returns True if Asian-fit frame variant is recommended.
    Combines regional origin with anatomical nasal root breadth.

    Asian-fit criteria:
      - nasal_root_breadth < 32 mm  →  low bridge, standard nose pads will slip
      - input_origin_region in ASIA_PACIFIC or INDIA  →  regional prior
    Either condition alone is sufficient to recommend Asian fit.
    """
    nasal_root      = dims["nasal_root_breadth"]["value"]
    regional_flag   = input_origin_region in ("ASIA_PACIFIC", "INDIA")
    anatomical_flag = nasal_root < 32.0

    return regional_flag or anatomical_flag

dims       = response["body_dimensions"]
asian_fit  = detect_asian_fit(dims, input_origin_region="ASIA_PACIFIC")
sku_suffix = "AF" if asian_fit else "STD"   # e.g. "FRAME-4821-AF" vs "FRAME-4821-STD"
```

> Regional origin is the broadest signal; `nasal_root_breadth` is the anatomical ground truth. A European customer with a low nasal bridge also benefits from an Asian-fit frame — the anatomical check catches cases the region alone misses.

<br>

## VR/AR Headset Strap & Seal Sizing

Map head dimensions to headset strap size and light-seal cushion variant:

```python
HEADSET_STRAP_SIZES = [
    # head_circumference thresholds (mm) — use upper range_95 bound
    (0,    530, "S"),
    (530,  570, "M"),
    (570,  610, "L"),
    (610, 9999, "XL"),
]

LIGHT_SEAL_VARIANTS = [
    # menton_sellion_length = face depth, chin to nose bridge (mm)
    (0,    115, "slim"),
    (115,  128, "standard"),
    (128, 9999, "deep"),
]

EAR_CUP_DEPTHS = [
    # ear_protrusion = how far the ear projects from the head (mm)
    # requires bundle: "FULL_BODY" or specific_dimensions: ["ear_protrusion"]
    (0,   18, "shallow"),    # ear cup depth ~18 mm sufficient
    (18,  24, "standard"),   # ear cup depth ~24 mm
    (24, 999, "deep"),       # ear cup depth ~30 mm — protruding ears need clearance
]

def lookup(value_mm, table):
    for lo, hi, label in table:
        if lo <= value_mm < hi:
            return label
    return "Unknown"

def size_vr_headset(dims):
    # Use upper range_95 bound for strap — too tight is a return; too loose is adjustable
    head_circ_upper = dims["head_circumference"]["range_95"][1]
    face_depth      = dims["menton_sellion_length"]["value"]

    result = {
        "strap_size":            lookup(head_circ_upper, HEADSET_STRAP_SIZES),
        "light_seal_variant":    lookup(face_depth, LIGHT_SEAL_VARIANTS),
        "head_circumference_mm": dims["head_circumference"]["value"],
        "face_depth_mm":         face_depth,
    }

    # ear_protrusion only available via FULL_BODY or specific_dimensions
    if "ear_protrusion" in dims:
        result["ear_cup_depth"] = lookup(dims["ear_protrusion"]["value"], EAR_CUP_DEPTHS)
        result["ear_protrusion_mm"] = dims["ear_protrusion"]["value"]

    return result

dims   = response["body_dimensions"]
vr_fit = size_vr_headset(dims)
```

<br>

## Response Handling Tips

- HEAD_FACE **BONE** dimensions (head_breadth, bizygomatic_breadth, face_length, head_length, menton_sellion_length) reach confidence ~85 at PRIMARY_BOTH tier. The single FLESH dimension relevant here — head_circumference — reaches ~78. Both tiers are sufficient for strap and frame size routing.
- Use `range_95` for boundary detection. If the interval for `bizygomatic_breadth` or `head_circumference` spans two size thresholds, present both options. For VR straps specifically, always use the upper `range_95` bound — a tight strap is a return; a loose one is adjustable.
- `nasal_root_breadth` is the correct input for Asian-fit SKU routing logic. `bridge_width` (nasal_root_breadth − 4 mm) is the correct value to display in UI copy such as "your bridge width is approximately X mm."
- The HEAD_FACE bundle returns **20 dimensions**. With `confidence_score_threshold: 0`, all 20 are available for client-side filtering — the payload is compact. To also retrieve the four ear and head-height dimensions (`ear_protrusion`, `ear_length`, `ear_breadth`, `tragion_top_of_head`), switch to `bundle: "FULL_BODY"` or add them explicitly to `specific_dimensions`. The FULL_BODY payload is significantly larger — use `specific_dimensions` if you only need HEAD_FACE plus the ear dims.
- For platforms serving ASIA_PACIFIC, INDIA, or MIDDLE_EAST: always pass `input_origin_region` per customer. Regional calibration has a proportionally larger effect on head and face dimensions than on body dimensions. Check `header.meta_warnings` for active fallback notices on partial-coverage regions (INDIA female, MIDDLE_EAST female fall back to GLOBAL coefficients).
- Flag any dimension with `biological_limit_status: "OUT_OF_BOUNDS"` before using it in fit routing — out-of-bounds values fall outside population normal range and should trigger a manual review prompt rather than an automated recommendation.

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
