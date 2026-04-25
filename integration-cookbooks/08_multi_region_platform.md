# Multi-Region Platform — Serving a Global Customer Base

<br>

## Business Context

**The Problem:** Global expansion and cross-border sourcing fail on a single issue: population-level skeletal proportions. 170 cm and 70 kg in Tokyo produces measurably different chest, waist, and shoulder dimensions than the same anchors in Berlin. Whether you serve a global audience or source from Asian factories for European customers, you're guessing your way through systematic population differences — and guessing is what keeps the return rate where it is.

**The Solution:** Fix it with one parameter: `input_origin_region`. The API interprets measurements in their correct proportional context and returns a complete, 130-point anthropometric profile in under 10ms. You see the actual physical dimensions the manufacturer intended, validate them against your target market, and get the ground truth before the bulk order goes out. No manual offset tables, no per-market code hacks.

**The Strategic Edge:** Use `target_region` to master cross-regional validation. Align predictions with your specific brand fit model, or compare the "Sourcing Delta" between two populations by calling the API twice with different regional settings. You identify fit gaps before committing to a bulk order or a new market launch. Which regional "M" fits your audience stops being a guess — it becomes a dimension-by-dimension comparison you can read in the response payload.

<br>

## How the Regional Calibration Works

```
Customer provides height + weight (from their regional context)
        │
        ▼
Step A — input_origin_region: "ASIA_PACIFIC"
  → Normalises input anchors to population-neutral ANSUR baseline
  → Eliminates systematic under/over-prediction for non-baseline populations
        │
        ▼
Ridge Regression Inference (ANSUR global baseline)
        │
        ▼
Step B — target_region: "EUROPE"  [optional advanced use]
  → Calibrates output proportions to the target population's norms
  → Relevant when your size system or recommendation engine was built on
    regional population data
        │
        ▼
Output: accurate body dimensions for this customer
```

**Why Step A matters — the Double Penalty Paradox:**
Without `input_origin_region`, an Asian customer's 162 cm height is interpreted by the ANSUR-trained model as "short person, smaller overall" — which underestimates every other dimension. The customer is penalised twice: once because the input anchor is regionally shorter for the same body type, and again because the model interprets that shorter anchor as a globally smaller frame. `input_origin_region` removes the first error before inference runs, so the regression operates on a correct baseline.

**When Step B changes the output meaningfully:**
`target_region` shifts proportional relationships in the output — for example, European bodies have different shoulder-to-hip ratios than Asian bodies at the same height. If your size chart was built from European measurements, calibrating output to `EUROPE` ensures the predicted dimensions sit in the same proportional space your size labels were defined in. For straightforward absolute-dimension comparisons (does this product's 96 cm chest opening fit this customer?), `target_region` matching the customer's region gives the most accurate absolute values.

<br>

## Regional Pairing Reference

| Scenario | `input_origin_region` | `target_region` | Notes |
|---|---|---|---|
| Any customer — correct absolute dimensions | Customer's region | Customer's region | Primary use case — most accurate absolute body measurements |
| Asian customer, European size chart | `ASIA_PACIFIC` | `EUROPE` | Use when your size labels were calibrated on European bodies |
| Indian customer, global platform | `INDIA` | `GLOBAL` | INDIA female: body measurements fall back to ASIA_PACIFIC |
| LATAM customer, US sizing | `LATAM` | `GLOBAL` | GLOBAL = ANSUR II (US Military) baseline |
| European customer, Japanese brand | `EUROPE` | `ASIA_PACIFIC` | Reverse cross-regional |
| Cross-regional sourcing comparison | Same age/demo | Vary between calls | Compare outputs to find population fit gaps before procurement |
| Unknown origin | `GLOBAL` | Brand's region | Safe default — no normalisation penalty applied |

<br>

## Sample Request — Asian Customer, Accurate Dimensions

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
        "exact_age": 31.0,
        "age_category": "ADULT",
        "input_origin_region": "ASIA_PACIFIC"
      },
      "anchors": {
        "body_height": 1620.0,
        "body_mass": 54.0
      }
    },
    "output_settings": {
      "calculation": {
        "calculation_model": "AUTO",
        "target_region": "ASIA_PACIFIC",
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

> To use the output against a European size chart calibrated on European bodies, change `target_region` to `"EUROPE"`. The `input_origin_region` stays `"ASIA_PACIFIC"` regardless — it reflects where the customer's measurements come from, not which size chart you're targeting.

<br>

## Sourcing Delta Pattern

Call the API twice for the same demographic with different `target_region` values. The difference between the two responses shows where population proportions diverge — and where a product sized for one market will or won't fit another.

```python
def sourcing_delta(gender, age, height_mm, mass_kg, source_region, target_region, bundle="TORSO"):
    """
    Returns the dimension-by-dimension delta between two regional profiles
    for the same demographic. Positive delta = target_region is larger.

    Typical use: source_region="ASIA_PACIFIC", target_region="EUROPE"
    → shows which dimensions of an Asian-sized product will be too small
      for a European customer of the same age/height/weight.
    """
    def build_request(region):
        return {
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
                    "body_mass": float(mass_kg)
                }
            },
            "output_settings": {
                "calculation": {
                    "calculation_model": "AUTO",
                    "target_region": region,
                    "body_build_type": "CIVILIAN"
                },
                "requested_dimensions": {"bundle": bundle},
                "output_format": {
                    "unit_system": "metric",
                    "confidence_score_threshold": 75,
                    "include_range_95": False,
                    "include_iso_codes": False
                }
            }
        }

    # → call API for build_request(source_region) and build_request(target_region)
    # dims_source = response_source["body_dimensions"]
    # dims_target = response_target["body_dimensions"]
    # delta = {}
    # for dim in dims_source:
    #     if dim in dims_target:
    #         delta[dim] = round(dims_target[dim]["value"] - dims_source[dim]["value"], 1)
    # return delta   # positive = target population is larger for this dimension


# Usage — European retailer evaluating Asian-manufactured workwear for European staff
# delta = sourcing_delta(
#     gender="male", age=35, height_mm=1750, mass_kg=78,
#     source_region="ASIA_PACIFIC", target_region="EUROPE",
# )
# A positive delta on chest_circumference means European bodies are larger at
# this height/weight — the Asian-sized product will be too narrow for this demographic.
```

> For product categories where multiple dimensions govern fit simultaneously (e.g., coveralls require chest + inseam + shoulder), check all governing dimensions against your product's tolerance range. A product may clear one dimension and fail another.

<br>

## Regional Coverage & Known Limitations

| Region | Coverage | Notes |
|---|---|---|
| `GLOBAL` | ✅ Full | ANSUR II reference population (US Military) |
| `EUROPE` | ✅ Full | Aggregated European datasets |
| `ASIA_PACIFIC` | ✅ Full | East Asian & Pacific datasets; includes WHO BMI offset (+2.0) |
| `LATAM` | ✅ Full | Latin American datasets |
| `INDIA` | ⚠️ Partial | Male: full. Female body measurements fall back to `ASIA_PACIFIC`; female head/face fall back to `GLOBAL`. WHO BMI offset (+1.5). Check `header.meta_warnings` |
| `AFRICA` | ⚠️ Partial — male only | Male-centric calibration; female body predictions use `GLOBAL` baseline with −10% confidence penalty on all FLESH dimensions |
| `MIDDLE_EAST` | ⚠️ Partial | Male-only coefficients validated for ages 18–30; female output extrapolated from male data |

> **For partial-coverage regions:** If your user base includes female customers from `AFRICA`, `INDIA`, or `MIDDLE_EAST`, surface the reduced accuracy in your UI — e.g., "Fit data for this region is limited. If you are between sizes, we recommend sizing up." Always check `header.meta_warnings` at runtime for active fallback notices.

<br>

## Multi-Tenant Platform Pattern

For a SaaS platform serving multiple retailers, derive `input_origin_region` from the customer's locale and `target_region` from the merchant's configuration:

```python
def get_prediction(customer_locale, merchant_config, gender, height_mm, mass_kg, age=None):
    """
    Build a DimensionsPot request for a cross-regional SaaS platform.

    customer_locale : ISO 3166-1 alpha-2 country code (e.g. 'JP', 'DE', 'BR')
    merchant_config : dict with 'size_chart_region' and optional 'body_build_type'

    input_origin_region is always derived from the customer's locale — this is the
    critical field for prediction accuracy. target_region is derived from the merchant's
    size chart calibration region.
    """
    LOCALE_TO_REGION = {
        "JP": "ASIA_PACIFIC", "KR": "ASIA_PACIFIC", "CN": "ASIA_PACIFIC",
        "TW": "ASIA_PACIFIC", "TH": "ASIA_PACIFIC", "VN": "ASIA_PACIFIC",
        "IN": "INDIA",
        "DE": "EUROPE", "FR": "EUROPE", "IT": "EUROPE", "ES": "EUROPE",
        "GB": "EUROPE", "NL": "EUROPE", "PL": "EUROPE", "SE": "EUROPE",
        "US": "GLOBAL", "CA": "GLOBAL", "AU": "GLOBAL",
        "BR": "LATAM", "MX": "LATAM", "CO": "LATAM", "AR": "LATAM",
        "SA": "MIDDLE_EAST", "AE": "MIDDLE_EAST", "EG": "MIDDLE_EAST",
        "NG": "AFRICA", "ZA": "AFRICA", "KE": "AFRICA",
    }

    input_region  = LOCALE_TO_REGION.get(customer_locale, "GLOBAL")
    target_region = merchant_config.get("size_chart_region", input_region)
    body_build    = merchant_config.get("body_build_type", "CIVILIAN")

    subject = {
        "gender": gender,
        "age_category": "ADULT",
        "input_origin_region": input_region,
    }
    if age is not None:
        subject["exact_age"] = float(age)

    return {
        "input_data": {
            "input_unit_system": "metric",
            "subject": subject,
            "anchors": {
                "body_height": float(height_mm),
                "body_mass": float(mass_kg)
            }
        },
        "output_settings": {
            "calculation": {
                "calculation_model": "AUTO",
                "target_region": target_region,
                "body_build_type": body_build
            },
            "requested_dimensions": {"bundle": "TORSO"},
            "output_format": {
                "unit_system": "metric",
                "confidence_score_threshold": 75,
                "include_range_95": True,
                "include_iso_codes": False
            }
        }
    }
```

> Note the `target_region` default: `input_region` (the customer's own region) rather than a hardcoded `"GLOBAL"`. This gives the most accurate absolute dimensions when the merchant has not specified a regional size chart calibration.

<br>

## Response Handling Tips

- `input_origin_region` is the accuracy-critical field. Getting this wrong produces systematic errors in every dimension for that customer. When the customer's region is unknown, `GLOBAL` is the safe default — it applies no normalisation and avoids the Double Penalty rather than risk applying the wrong regional correction.
- `target_region` changes the proportional calibration of the output. Store both `input_origin_region` and `target_region` alongside every saved dimensional profile — a `chest_circumference` calibrated for `EUROPE` is a numerically different value than the same customer's `chest_circumference` calibrated for `ASIA_PACIFIC`.
- Check `header.modifiers_applied` in every response — it lists the exact calibration steps applied, including which regional coefficients were used. Essential for debugging when output values differ from a naive estimate.
- Check `header.meta_warnings` for regional fallback notices (e.g., India female fallback to ASIA_PACIFIC). These are non-fatal but indicate reduced regional accuracy for that specific request.
- When `input_origin_region == target_region`, both normalisation steps still apply — Step A normalises to the ANSUR baseline and Step B calibrates back to the same region. This is the correct approach for all requests, including same-region ones. Do not omit either parameter.
- Response time is unaffected by cross-regional requests. The translation steps are coefficient lookups, not additional model calls. P99 latency remains 6–8 ms regardless of the regional combination.
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