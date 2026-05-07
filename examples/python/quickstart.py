# Replace YOUR_API_KEY with your RapidAPI key
# Get your key at: https://rapidapi.com/d-pot-apps/api/dimensionspot-bodysize-engine

import requests

URL = "https://dimensionspot-bodysize-engine.p.rapidapi.com/v1/predict"
HEADERS = {
    "X-RapidAPI-Key": "YOUR_API_KEY",
    "X-RapidAPI-Host": "dimensionspot-bodysize-engine.p.rapidapi.com",
    "Content-Type": "application/json",
}

payload = {
    "input_data": {
        "input_unit_system": "metric",
        "subject": {
            "gender": "male",
            "exact_age": 35.0,
            "age_category": "ADULT",
            "input_origin_region": "EUROPE",
        },
        "anchors": {
            "body_height": 1780,  # millimeters — NOT centimeters (178 cm × 10)
            "body_mass": 82.0,    # kilograms
        },
    },
    "output_settings": {
        "calculation": {
            "calculation_model": "AUTO",
            "target_region": "EUROPE",
            "body_build_type": "CIVILIAN",
        },
        "requested_dimensions": {"bundle": "FULL_BODY"},
        "output_format": {
            "unit_system": "metric",
            "confidence_score_threshold": 0,
            "include_range_95": True,
            "include_iso_codes": True,
        },
    },
}

response = requests.post(URL, json=payload, headers=HEADERS)
response.raise_for_status()
data = response.json()

dimensions = data["body_dimensions"]
print(f"Engine used: {data['header']['calculation_model_used']}")
print(f"Dimensions returned: {len(dimensions)}\n")

# Print a sample of key dimensions
for key in ["shoulder_height", "chest_circumference", "waist_circumference_omphalion", "hip_circumference"]:
    if key in dimensions:
        dim = dimensions[key]
        print(
            f"{dim['label']}: {dim['value']} {dim['unit']} "
            f"(confidence: {dim['confidence_score']}, "
            f"range_95: {dim['range_95']})"
        )
