#!/usr/bin/env bash
# Replace YOUR_API_KEY with your RapidAPI key
# Get your key at: https://rapidapi.com/d-pot-apps/api/dimensionspot-bodysize-engine

API_KEY="YOUR_API_KEY"

# Full body profile — height + weight, European adult male
# Note: body_height is in millimeters (1780 mm = 178 cm)

curl -s -X POST "https://dimensionspot-bodysize-engine.p.rapidapi.com/v1/predict" \
  -H "Content-Type: application/json" \
  -H "X-RapidAPI-Key: $API_KEY" \
  -H "X-RapidAPI-Host: dimensionspot-bodysize-engine.p.rapidapi.com" \
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
        "bundle": "FULL_BODY"
      },
      "output_format": {
        "unit_system": "metric",
        "confidence_score_threshold": 0,
        "include_range_95": true,
        "include_iso_codes": true
      }
    }
  }' | python3 -m json.tool

# --- Minimal request (all output_settings are optional) ---
#
# curl -s -X POST "https://dimensionspot-bodysize-engine.p.rapidapi.com/v1/predict" \
#   -H "Content-Type: application/json" \
#   -H "X-RapidAPI-Key: $API_KEY" \
#   -H "X-RapidAPI-Host: dimensionspot-bodysize-engine.p.rapidapi.com" \
#   -d '{"input_data": {"subject": {"gender": "male"}, "anchors": {"body_height": 1780}}}'

# --- Liveness check ---
#
# curl -s "https://dimensionspot-bodysize-engine.p.rapidapi.com/health" \
#   -H "X-RapidAPI-Key: $API_KEY" \
#   -H "X-RapidAPI-Host: dimensionspot-bodysize-engine.p.rapidapi.com"

# --- Capability discovery (all enum values) ---
#
# curl -s "https://dimensionspot-bodysize-engine.p.rapidapi.com/v1/info" \
#   -H "X-RapidAPI-Key: $API_KEY" \
#   -H "X-RapidAPI-Host: dimensionspot-bodysize-engine.p.rapidapi.com" | python3 -m json.tool
