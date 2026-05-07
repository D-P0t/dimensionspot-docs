# Replace YOUR_API_KEY with your RapidAPI key
# Demonstrates the pediatric engine (LMS Box-Cox, calibrated to CDC/WHO growth standards).
# Use case: childrenswear sizing, pediatric product design, clinical growth tracking.

import requests

URL = "https://dimensionspot-bodysize-engine.p.rapidapi.com/v1/predict"
HEADERS = {
    "X-RapidAPI-Key": "YOUR_API_KEY",
    "X-RapidAPI-Host": "dimensionspot-bodysize-engine.p.rapidapi.com",
    "Content-Type": "application/json",
}

# Pediatric engine activates automatically when exact_age <= 20.
# body_height and body_mass are OUTPUTS in pediatric mode (derived from CDC LMS tables),
# not required inputs. Supply them only if you want to override the CDC-predicted values.

payload = {
    "input_data": {
        "input_unit_system": "metric",
        "subject": {
            "gender": "female",
            "exact_age": 8.0,       # exact_age strongly recommended for pediatric — growth rates are high
            "age_category": "CHILD",
            "input_origin_region": "GLOBAL",
        },
        "anchors": {},  # no anchors needed — CDC LMS method derives height and mass from age + sex
    },
    "output_settings": {
        "calculation": {
            "calculation_model": "AUTO",  # routes to PEDIATRIC because exact_age <= 20
            "target_region": "GLOBAL",
            "body_build_type": "CIVILIAN",
        },
        "requested_dimensions": {"bundle": "FULL_BODY"},
        "output_format": {
            "unit_system": "metric",
            "confidence_score_threshold": 0,
            "include_range_95": True,
            "include_iso_codes": False,
        },
    },
}

response = requests.post(URL, json=payload, headers=HEADERS)
response.raise_for_status()
data = response.json()

header = data["header"]
print(f"Engine used: {header['calculation_model_used']}")  # PEDIATRIC
# anchors_calculated is False for pediatric — the LMS engine is not the imputation pipeline.
# body_height and body_mass are predicted by the LMS engine and appear in body_dimensions,
# not in calculated_anchors (which is always {} for pediatric requests).
print(f"Anchors imputed: {header['anchors_calculated']}")  # False
print(f"Warnings: {header['meta_warnings'] or 'none'}\n")

dimensions = data["body_dimensions"]
# LMS-derived dimensions: body_height (BONE, conf 99), body_mass (FLESH, conf 99),
#   head_circumference (FLESH, conf 99) — exact tabular norms, not regression estimates.
# Ridge-derived dimensions (all others): capped at confidence 80 in pediatric mode.
for key in ["body_height", "body_mass", "head_circumference", "shoulder_height", "foot_length"]:
    if key in dimensions:
        dim = dimensions[key]
        print(
            f"{dim['label']}: {dim['value']} {dim['unit']} "
            f"(confidence: {dim['confidence_score']}, type: {dim['type']})"
        )
