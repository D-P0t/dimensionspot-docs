# Replace YOUR_API_KEY with your RapidAPI key
# Demonstrates cross-regional calibration: input from one population, output for another.
# Use case: Asian customer shopping a European brand's size chart.

import requests

URL = "https://dimensionspot-bodysize-engine.p.rapidapi.com/v1/predict"
HEADERS = {
    "X-RapidAPI-Key": "YOUR_API_KEY",
    "X-RapidAPI-Host": "dimensionspot-bodysize-engine.p.rapidapi.com",
    "Content-Type": "application/json",
}

# input_origin_region: the population your customer belongs to (normalizes anchor values)
# target_region: the population your size chart was built for (calibrates output proportions)
# These are independent — setting both enables the Universal Translator (cross-regional).

payload = {
    "input_data": {
        "input_unit_system": "metric",
        "subject": {
            "gender": "female",
            "exact_age": 28.0,
            "age_category": "ADULT",
            "input_origin_region": "ASIA_PACIFIC",  # customer's origin
        },
        "anchors": {
            "body_height": 1620,  # mm
            "body_mass": 55.0,    # kg
        },
    },
    "output_settings": {
        "calculation": {
            "calculation_model": "AUTO",
            "target_region": "EUROPE",  # brand's size chart origin
            "body_build_type": "CIVILIAN",
        },
        "requested_dimensions": {
            "bundle": "TORSO",  # clothing-relevant: chest, waist, hip, shoulder, sitting heights
        },
        "output_format": {
            "unit_system": "metric",
            "confidence_score_threshold": 75,  # retains FLESH dims at PRIMARY_BOTH (~78)
            "include_range_95": True,
            "include_iso_codes": False,
        },
    },
}

response = requests.post(URL, json=payload, headers=HEADERS)
response.raise_for_status()
data = response.json()

print(f"Modifiers applied: {data['header']['modifiers_applied']}")
print(f"Warnings: {data['header']['meta_warnings'] or 'none'}\n")

dimensions = data["body_dimensions"]
for key in ["chest_circumference", "waist_circumference_omphalion", "hip_circumference"]:
    if key in dimensions:
        dim = dimensions[key]
        print(f"{dim['label']}: {dim['value']} {dim['unit']} (confidence: {dim['confidence_score']})")
